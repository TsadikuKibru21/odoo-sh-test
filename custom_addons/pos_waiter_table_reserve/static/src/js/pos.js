/** @odoo-module */
console.log("POSSSSSS ")

import { models } from "@point_of_sale/app/store/models";
import { Table } from "@pos_restaurant/app/floor_screen/table";

console.log("POSSSSSS1 ")

console.log("@@@@@@@@@@",models)
// export class models2 extends PosModel.prototype.models {
//     constructor() {
//         super(...arguments);
//         this._overrideRestaurantFloorModelDomain();
//     }
//     _overrideRestaurantFloorModelDomain() {
//         const models2 = this.models;
//         for (let i = 0; i < models2.length; i++) {
//             const model = models2[i];
//             if (model.model === 'restaurant.floor') {
//                 model.domain = function (self) {
//                     return [['pos_config_id2', 'in', self.config.id]];
//                 };
//             }
//         }
//     }
// }
//     export class Table2 extends Table {


//     // const PosResTableWidget = TableWidget => class extends TableWidget {
//             mounted() {
//                 const table = this.props.table;
//                 function unit(val) {
//                     return `${val}px`;
//                 }
//                 const style = {
//                     width: unit(table.width),
//                     height: unit(table.height),
//                     'line-height': unit(table.height),
//                     top: unit(table.position_v),
//                     left: unit(table.position_h),
//                     'border-radius': table.shape === 'round' ? unit(1000) : '3px',
//                 };
//                 var table_data = this.env.pos.pos_table_data;
//                 var temp = false;
//                 var user = this.env.pos.get_cashier();
//                 for(var i=0;i<table_data.length;i++){
//                     if(table_data[i]['table_id'] == table.id){
                        
//                         if(user.user_id[0] != table_data[i]['user_id']){
//                             temp = true;
//                         }
//                     }
//                 }
//                 if(temp){
//                     style.background = 'red';
//                 }
//                 else{
//                     if (table.color) {
//                         style.background = table.color;
//                     }
//                 }
//                 if (table.height >= 150 && table.width >= 150) {
//                     style['font-size'] = '32px';
//                 }
//                 Object.assign(this.el.style, style);

//                 const tableCover = this.el.querySelector('.table-cover');
//                 Object.assign(tableCover.style, { height: `${Math.ceil(this.fill * 100)}%` });
//             }
//         }



        // patch(Order.prototype, {

        //     // models.Order =  models.Order.extend({
        //             initialize: function(attr, options) {
        //                 _super_order.initialize.call(this,attr,options);
        //                 _super_order.initialize.apply(this, arguments);
        //                 this.uiState = {
        //                     ReceiptScreen: new Context({
        //                         inputEmail: '',
        //                         emailSuccessful: null,
        //                         emailNotice: '',
        //                     }),
        //                     TipScreen: new Context({
        //                         inputTipAmount: '',
        //                     }),
        //                     PaymentScreen: new Context({
        //                         inputPhoneNumber: '',
        //                     }),
        //                 };
        //             },
            
            
        //         });


        // };

    // Registries.Component.extend(TableWidget, PosResTableWidget);
    // var PosModelSuper = models.PosModel;

    // models.PosModel = models.PosModel.extend({
    //     // patch PosModel extends models.PosModel.prototype.models {

    //     initialize: function(session, attributes) {
    //         this.pos_table_data = [];
    //         var self = this;
    //         PosModelSuper.prototype.initialize.call(this,session,attributes);
    //         this.ready.then(function () {
    //             if(! self.config.allow_waiter_reservation){
    //                 return
    //             }
    //             var channel_name = "wv_pos_table_data_sess";
    //             var callback = function(bus_message){
    //                 if(bus_message.type=="reserve"){
    //                     var temp = true;
    //                     for(var i=0;i<self.pos_table_data.length;i++){
    //                         if(self.pos_table_data[i]['table_id'] == bus_message.data.table_id){
    //                             temp=false;
    //                         }
    //                     }
    //                     if(temp){
    //                         self.pos_table_data.push(bus_message.data)
    //                     }
    //                 }
    //                 if(bus_message.type =="remove"){
    //                     var all_data = self.pos_table_data;
    //                     for(var i=0;i<all_data.length;i++){
    //                         if(all_data[i]['table_id'] == bus_message.data.table_id){
    //                             self.pos_table_data.splice(i, 1);
    //                         }
    //                     }
    //                 }
                 
    //             }
    //             self.bus.add_channel_callback(channel_name, callback, self);
    //             if (self.config.sync_server){
    //                 self.add_bus('sync_server', self.config.sync_server);
    //                 self.get_bus('sync_server').add_channel_callback(channel_name, callback, self);
    //                 self.sync_bus = self.get_bus('sync_server');
    //                 self.get_bus('sync_server').start();
    //             } else {
    //                 self.sync_bus = self.get_bus();
    //                 if (!self.config.autostart_longpolling) {
    //                     self.sync_bus.start();
    //                 }
    //             }
    //         });
    //     },
    //     set_table (table) {
    //         var self = this;
    //         if (!table) {
    //             var orders = this.get_order_list();
    //             if(orders.length == 0){
    //                 var user = this.get_cashier()
    //                 self.rpc({
    //                   model: 'pos.config',
    //                   method: 'sync_table_data',
    //                   args: ['remove', {"table_id":this.table.id,"user_id":user.user_id[0],"user_name":user.name}],
    //               }).then(function (result) {
    //               }); 
    //             }
    //             this.set_order(null);
    //         } else if (this.order_to_transfer_to_different_table) {
    //             this.order_to_transfer_to_different_table.table = table;
    //             this.order_to_transfer_to_different_table.save_to_db();
    //             this.order_to_transfer_to_different_table = null;
    //             this.set_table(table);

    //         } else {
    //             var temp = true;
    //             var user = this.get_cashier();
    //             for(var i=0;i<this.pos_table_data.length;i++){                    
    //                 if(this.pos_table_data[i]['table_id'] == table.id){
    //                     if(this.pos_table_data[i]['user_id'] == user.user_id[0]){
    //                         temp = true;
    //                         break
    //                     }
    //                     else{
    //                         temp = false;
    //                     }
    //                 }
    //             }
    //             if(temp){                    
    //                 self.rpc({
    //                       model: 'pos.config',
    //                       method: 'sync_table_data',
    //                       args: ['reserve', {"table_id":table.id,"user_id":user.user_id[0],"user_name":user.name}],
    //                   }).then(function (result) {
    //                   });
    //                   this.table = table;
    //                     var orders = this.get_order_list();
    //                     if (orders.length) {
    //                         this.set_order(orders[0]); 
    //                     } else {
    //                         this.add_new_order(); 
    //                     }
    //             }
    //             else{
    //                 alert("Sorry this Table is already Reserved.");
    //             }
    //         }
    //     },
    //     get_cashier_name (table_id) {
    //             var self = this;
    //             var table_data = self.env.pos.pos_table_data;
    //             for(var i=0;i<table_data.length;i++){
    //                 if(table_data[i]['table_id'] == table_id){
    //                     return table_data[i]['user_name']
    //                 }
    //             }
    //             return ""
    //         }
    // });

