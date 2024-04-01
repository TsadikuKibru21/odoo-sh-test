/** @odoo-module */

import { PaymentInterface } from "@point_of_sale/app/payment/payment_interface";
import { jsonrpc } from "@web/core/network/rpc_service";
import { _t } from "@web/core/l10n/translation";
import { useService } from "@web/core/utils/hooks";
import { usePos } from "@point_of_sale/app/store/pos_hook";


export class PaymentTelebirr extends PaymentInterface {

    setup() {
        super.setup(...arguments);
    }




  async  _telebirr_pay () {
    console.log("yyyyyyyyyyyyy",this.pos.get_order().uiState.PaymentScreen.Phone)
    const phone = this.pos.get_order().uiState.PaymentScreen.Phone
    console.log("POssss",this.pos)
    console.log("::::::::::",this.pos.pos_session.config_id[0])
    console.log(this.payment_method.telebirr_app_id)
    // const phone = this.env.utils.isValidFloat(order.uiState.ProductScreen.Phone)
// console.log("phoneeee", this.orderUiState.Phone)
    // paymentScreenPaymentLines.checkPaymentStatus();
    console.log("PAYMENT METHOD", this.payment_method)


        console.log('_telebirr_pay', 'THIS', this.pos.get_order().booked)
        var self = this;
        var order = this.pos.get_order();
        if (order.selected_paymentline.amount < 0) {
            this._show_error(_t('Cannot process transactions with negative amount.'));
          
        }
        var uid = order.uid.replace(/-/g, '')
        console.log(uid)
        var config = this.pos.config;
        var random_val = Math.floor(Math.random() * 10000);
        console.log(order.uiState)
        var trace_no = random_val.toString().concat("_", uid);
        var data = {
            "payerId": this.payment_method.telebirr_app_id,
            "pos_session": this.pos.pos_session.config_id[0],
            "traceNo": trace_no,
            "amount": order.selected_paymentline.amount,
            "phone": phone
        }
        // var data = "LLLLLLLL"
       console.log("PAYERRRR")
       console.log(this.payment_method)
       let info_data= await this._call_telebirr(data);
       console.log("IIIIIIIIIIIIIII",info_data.msg)
       return self._telebirr_handle_response(info_data);
    }

    
    send_payment_request (cid) {
        this._super.apply(this, arguments);
        console.log('TESTE', cid)
        this._reset_state();
        return this._telebirr_pay();
    }
    async send_payment_cancel (order, cid) {
        super.send_payment_cancel(...arguments);
        return true;
    }
    close () {
        this._super.apply(this, arguments);
    }


    // async _call_telebirr (data, operation) {
    //                try{
    //                    let  info_data = await jsonrpc(`/send_request_telebirr`, {data
    //                     });
    //                     console.log("PPPPPPPPPPP",info_data.msg)
                        
    //                     return info_data;
    //                 } catch (error) {
    //                     // Handle errors
    //                     console.error('Error:', error);
    //                     throw error; // Optionally rethrow the error
    //                 }
    // }

    async _call_telebirr(data1,operation) {
        console.log("AAAAAAAAAAAAAA")
            const amount = 3;
            const data = await this.env.services.orm.silent.call(
                'pos.payment.method',
                'send_request_telebirr',
                [[this.payment_method.id], data1],

            );
            if (data?.error) {
                throw data.error;
            }
            return data;
    }
   
    send_payment_request(cid) {
                console.log("@@@!!!!")
                console.log(this.payment_method)
                super.send_payment_request(cid);
                return this._telebirr_pay(cid);
            }
  
    // async  _telebirr_handle_response (response) {

    //     var line = this.pos.get_order().selected_paymentline;
    //     line.set_payment_status('done');

    //     if(response.msg==='Success'){
    //         console.log("??????",response.msg)
    //         line.set_payment_status('done');
    //          console.log(line)

    //     }


    //           }
    _reset_state () {
        this.was_cancelled = false;
        this.last_diagnosis_service_id = false;
        this.remaining_polls = 4;
        clearTimeout(this.polling);
    }
    _telebirr_handle_response (response) {
        var line = this.pos.get_order().selected_paymentline;

        console.log('_telebirr_handle_response', this.pos.get_order(), 'UIO', this.pos.pos_session.config_id[0])

       
            line.set_payment_status('waitingCard');
            if (response.status_code == 401) {
                this._show_error(_t('Authentication failed. Please check your Telebirr credentials.'));
                line.set_payment_status('force_done');
                return Promise.resolve();
            }else{
            var self = this;
            var res = new Promise(function (resolve, reject) {
                // clear previous intervals just in case, otherwise
                // it'll run forever
                clearTimeout(self.polling);

                self.polling = setInterval(function () {
                    self._poll_for_response(resolve, reject);
                }, 3000);
            });

            // make sure to stop polling when we're done
            res.finally(function () {
                self._reset_state();
            });

            return res;
            }
    }
    
    _telebirr_cancel (ignore_error) {
        this._reset_state();
        var order = this.pos.get_order();
        var line = order.selected_paymentline;
        console.log(line, '_telebirr_cancel');
        if (line) {
            line.set_payment_status('retry');
        }
        return Promise.reject();
    }
    // _poll_for_response (resolve, reject) {
    //     var self = this;
    //     var line = this.pos.get_order();
    //     var pos_ses = this.pos.pos_session.config_id[0];
    //     console.log("@@@@@@@@@@@@@@@@", pos_ses);
    //     console.log(line, '_poll_for_response', pos_ses);
        
    //     if (this.was_cancelled) {
    //         resolve(false);
    //         return Promise.resolve();
    //     }
        
    //     var trace_id = this.payment_method.telebirr_payment;
        
    //     // Make the JSON-RPC call
    //     return jsonrpc('/    ', {
    //         tt: this.payment_method.id,
    //         pos_ses: pos_ses
    //     }, {
    //         timeout: 3000,
    //         shadow: true
    //     }).catch(function (error) {
    //         if (self.remaining_polls != 0) {
    //             self.remaining_polls--;
    //         } else {
    //             reject();
    //             self.poll_error_order = self.pos.get_order();
    //             return self._handle_odoo_connection_failure(error);
    //         }
    //         // Ensure the promise is rejected if error occurs
    //         throw error;
    //     }).then(function (status) {
    //         console.log("O3333333333333333333333333333");
    //         if (status) {
    //             var notification = status.trace_no;
    //             var order = self.pos.get_order();
    //             var line = order.selected_paymentline;
    //             console.log("!!!!!!!!!!!!!!!!!!!!!!!!!!!", status);
    //             if (status.msg !== '') {
    //                 if (status.msg == 'Success') {
    //                     console.log("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOO");
    //                     line.set_payment_status('done');
    //                     return Promise.resolve()
                        
                      
    //                     // resolve(true);
    //                 } else {
    //                     self._show_error(_.str.sprintf(_t('Message from Telebirr: %s'), status.msg));
    //                     // This means the transaction was cancelled by pressing the cancel button on the device
    //                     line.set_payment_status('retry');
    //                     reject();
    //                 }
    //             } else if (status.msg == '') {
    //                 self._show_error(_t('The connection to your payment terminal failed. Please check if it is still connected to the internet.'));
    //                 self._telebirr_cancel();
    //                 resolve(false);
    //             }
    //         }
    //     });
    // }
    // _poll_for_response(resolve, reject) {
    //     var self = this;
    //     var line = this.pos.get_order().selected_paymentline;
    //     var pos_ses = this.pos.pos_session.config_id[0];
    //     console.log("@@@@@@@@@@@@@@@@", pos_ses);
    //     console.log(line, '_poll_for_response', pos_ses);
    
    //     if (this.was_cancelled) {
    //         resolve(false);
    //         return Promise.resolve();
    //     }
    
    //     var trace_id = this.payment_method.telebirr_payment;
    
    //     // Make the JSON-RPC call
    //     return jsonrpc('/find_pay_confirmed_telebirr', {
    //         tt: this.payment_method.id,
    //         pos_ses: pos_ses
    //     },
    //     {
    //         timeout: 3000,
    //         shadow: true
    //     })
    //     .catch(function (error) {
    //         if (self.remaining_polls != 0) {
    //             self.remaining_polls--;
    //         } else {
    //             reject();
    //             self.poll_error_order = self.pos.get_order();
    //             return self._handle_odoo_connection_failure(error);
    //         }
    //         // Ensure the promise is rejected if an error occurs
    //         throw error;
    //     })
    //     .then(function (status) {
    //         console.log("O3333333333333333333333333333");
    //         if (status) {
    //             var notification = status.trace_no;
    //             var order = self.pos.get_order();
    //             console.log("!!!!!!!!!!!!!!!!!!!!!!!!!!!", status);
    //             if (status.msg !== '') {
    //                 if (status.msg == 'Success') {
    //                     console.log("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOO");
    //                     // line.set_payment_status('done');
    //                     // Stop polling by resolving the promise
    //                    return resolve(true);
    //                 } else {
    //                     console.log("errr")
    //                     // self._show_error(_.str.sprintf(_t('Message from Telebirr: %s'), status.msg));
    //                     // This means the transaction was canceled by pressing the cancel button on the device
    //                     line.set_payment_status('retry');
    //                     return resolve(false);
    //                 }
    //             } else if (status.msg == '') {
    //                 self._show_error(_t('The connection to your payment terminal failed. Please check if it is still connected to the internet.'));
    //                 self._telebirr_cancel();
    //                 resolve(false);
    //             }
    //         }
    //     });
    // }


    _poll_for_response(resolve, reject) {
        var self = this;
        var line = this.pos.get_order().selected_paymentline;
        var pos_ses = this.pos.pos_session.config_id[0];
        console.log("@@@@@@@@@@@@@@@@", pos_ses);
        console.log(line, '_poll_for_response', pos_ses);
    
        if (this.was_cancelled) {
            resolve(false);
            return Promise.resolve();
        }
    
        var trace_id = this.payment_method.telebirr_payment;
    
        // Define a function to make the ORM call
        function makeOrmCall() {
            return self.env.services.orm.silent.call(
                'pos.payment.method',
                'find_pay_confirmed_telebirr',

                [[self.payment_method.id], pos_ses]
            );
        }
    
        // Create a promise that resolves when either the ORM call resolves or the timeout is reached
        var timeoutPromise = new Promise(function (resolve, reject) {
            setTimeout(function () {
                reject(new Error('ORM call timed out'));
            }, 30000); // Set timeout to 3000 milliseconds
        });
    
        return Promise.race([makeOrmCall(), timeoutPromise])

        // return Promise.race([makeOrmCall()])
            .then(function (status) {
                console.log("O3333333333333333333333333333");
                if (status) {
                    var notification = status.trace_no;
                    var order = self.pos.get_order();
                    console.log("!!!!!!!!!!!!!!!!!!!!!!!!!!!", status);
                    if (status.msg !== '') {
                        if (status.msg == 'Success') {
                            console.log("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOO");
                            // line.set_payment_status('done');
                            // Stop polling by resolving the promise
                            return resolve(true);
                        } else {
                            console.log("errr")
                            // self._show_error(_.str.sprintf(_t('Message from Telebirr: %s'), status.msg));
                            // This means the transaction was canceled by pressing the cancel button on the device
                            line.set_payment_status('retry');
                            return resolve(false);
                        }
                    } else if (status.msg == '') {
                        self._show_error(_t('The connection to your payment terminal failed. Please check if it is still connected to the internet.'));
                        self._telebirr_cancel();
                        resolve(false);
                    }
                }
            })
            .catch(function (error) {
                if (self.remaining_polls != 0) {
                    self.remaining_polls--;
                } else {
                    reject();
                    self.poll_error_order = self.pos.get_order();
                    return self._handle_odoo_connection_failure(error);
                }
                // Ensure the promise is rejected if an error occurs
                throw error;
            });
    }


    


//   async  _telebirr_handle_response (response) {
//         console.log("RESPONSEEEEEEE")
//         console.log(response)
//         var line = this.pos.get_order().selected_paymentline;
//         console.log('_telebirr_handle_response',response.msg)

//         // if (response.status_code == 401) {
//         //     this._show_error(_t('Authentication failed. Please check your Telebirr credentials.'));
//         //     line.set_payment_status('force_done');
    
//         // }

//         // if (response.msg && response.msg !== 'Success') {
//         //     if (response.msg !== 'Success') {

//         //     console.error('error from Telebirr', response.msg);

//         //     var msg = '';

//         //     this._show_error(_.str.sprintf(_t('An unexpected error occured. Message from Telebirr: %s'), response.response));
//         //     if (line) {
//         //         line.set_payment_status('force_done');
//         //     }

//         // } else {
          
//             if(response.msg==='Success'){
//                 console.log("sssssssssswwwwww")
//                 // line.set_payment_status('done')
               
//                 // this.set_payment_status("waiting");
//                 console.log(line.payment_status)
//                 const paymentScreenPaymentLines = new PaymentScreenPaymentLines(); // Instantiate paymentScreenPaymentLines

//                 // Assuming paymentScreenPaymentLines is properly imported or defined elsewhere
//                 if (paymentScreenPaymentLines) {
//                     line.set_payment_status("waitingCard");

//                     paymentScreenPaymentLines.checkPaymentStatus().then(confirmation => {

//                     console.log("???????????/",confirmation)
//                     if (confirmation == "Success") {

//                         // const paymentScreenPaymentLines = new PaymentScreenPaymentLines();

//                         console.log("Successfully paid");
//                         line.set_payment_status('done')
//                         console.log("MMMMMMMMMM66oM",line)
//                     } else {
//                         self._show_error(_.str.sprintf(_t('Message from Telebirr: %s'), confirmation));
//                         line.set_payment_status('retry');
//                     }
                    
//                 }).catch(error => {
//                     // Handle error
//                     console.error("Error checking payment status:", error);
//                 });
//             }


//         }
//                 }
_telebirr_cancel (ignore_error) {
    this._reset_state();
    var order = this.pos.get_order();
    var line = order.selected_paymentline;
    console.log(line, '_telebirr_cancel');
    if (line) {
        line.set_payment_status('retry');
    }
    return Promise.reject();
}

_show_error (msg, title) {
    if (!title) {
        title =  _t('Telebirr Error');
    }
    Gui.showPopup('ErrorPopup',{
        'title': title,
        'body': msg,
    });
}

    async pay() {
        console.log("$$$$$$$$$$$$Payyy111()",this.payment_method.payment_terminal)
        this.set_payment_status("waiting");
        return this.handle_payment_response(
            await this.send_payment_request(this.cid)
        );
    }


}
// });

