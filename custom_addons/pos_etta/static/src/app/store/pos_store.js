/** @odoo-module */
import { patch } from "@web/core/utils/patch";
import { PosStore } from "@point_of_sale/app/store/pos_store";

patch(PosStore.prototype, {
    async setup() {
        this.is_refund = false;
        await super.setup(...arguments);
    },
    is_refund_order() {
        return this.is_refund;
    },
    set_is_refund_order(value) {
        this.is_refund = value;
    },
    getFormattedDate() {
        // Get today's date
        var today = new Date();

        // Get day, month, and year components
        var day = today.getDate();
        var month = today.getMonth() + 1; // Month is zero-based, so add 1
        var year = today.getFullYear();

        // Pad day and month with leading zeros if needed
        if (day < 10) {
            day = '0' + day;
        }
        if (month < 10) {
            month = '0' + month;
        }

        // Format the date as dd/mm/yyyy
        var formattedDate = day + '/' + month + '/' + year;

        return formattedDate;
    },
    async printZReport() {
        if (!this.correctTimeConfig()) {
            this.env.services.notification.add("Time mismatch between server and fiscal printer", {
                type: 'danger',
                sticky: false,
                timeout: 10000,
            });
            return;
        }
        if (window.Android != undefined) {
            if (window.Android.isAndroidPOS()) {
                var result = window.Android.printZReport();

                this.makeLogEntry("Z Report Printed Request");

                var responseObject = JSON.parse(result);

                if (responseObject.success) {

                    this.env.services.notification.add("Z Report Printed", {
                        type: 'info',
                        sticky: false,
                        timeout: 10000,
                    });

                    this.makeLogEntry("Z Report Printed");

                    this.uploadTodayEj();
                }
                else {

                    this.env.services.notification.add(responseObject.message, {
                        type: 'danger',
                        sticky: false,
                        timeout: 10000,
                    });

                    this.makeLogEntry("Z Report Printing Failed");
                }

            }
        }

    },
    async correctTimeConfig() {
        const serverTime = await this.getServerTime();

        // If there was a network error, serverTime would be true, and we skip comparison
        if (serverTime === true) {
            // console.log("Network error encountered, skipping time comparison.");
            return true;
        }

        const serverDate = new Date(serverTime);
        const deviceDate = new Date();
        const timeDiff = Math.abs(serverDate - deviceDate);
        const timeDiffInMinutes = timeDiff / 60000;

        // console.log("Time Difference (minutes):", timeDiffInMinutes);

        // Define your acceptable threshold in minutes (e.g., 5 minutes)
        const thresholdMinutes = 5;

        // Check if the time difference is within the acceptable range
        if (timeDiffInMinutes > thresholdMinutes) {
            // // console.warn("Significant time difference detected.");
            
            this.env.services.notification.add("TIME MISMATCH \n Server : " + serverDate + "\n Device : " + deviceDate + " Diff : " + timeDiffInMinutes, {
                type: 'danger',
                sticky: false,
                timeout: 10000,
            });

            return false;
        } else {
            // // console.log("Time difference is within acceptable range.");
            return true;
        }
    },
    async getServerTime() {
        // try {
        //     const response = await this.orm.call("pos.session", "get_server_time", []);
        //     // console.log(response);
        //     return response;
        // } catch (error) {
        //     // console.error("Failed to get server time:", error);
        //     return true;
        // }
        return true;
    },
    async printXReport() {
        if (!this.correctTimeConfig()) {
            return;
        }
        if (window.Android != undefined) {
            if (window.Android.isAndroidPOS()) {
                var log_data;
                var result = window.Android.printXReport();

                this.makeLogEntry("X Report Printing Request");

                var responseObject = JSON.parse(result);

                if (responseObject.success) {
                    this.env.services.notification.add("X Report Printed", {
                        type: 'info',
                        sticky: false,
                        timeout: 10000,
                    });

                    this.makeLogEntry("X Report Printed");
                }
                else {
                    this.env.services.notification.add("X Report Printing Failed", {
                        type: 'danger',
                        sticky: false,
                        timeout: 10000,
                    });
                    this.makeLogEntry("X Report Printing Failed");
                }
            }
        }
    },
    uploadTodayEj() {
        if (window.Android != undefined) {
            if (window.Android.isAndroidPOS()) {
                var fromDate = this.getFormattedDate();
                var toDate = this.getFormattedDate();
                var formatedData = {
                    from_date: fromDate,
                    to_date: toDate
                }
                this.makeLogEntry("EJ Upload Request Data -> " + JSON.stringify(formatedData));
                window.Android.uploadEJ(JSON.stringify(formatedData));
            }
        }
    },
    makeLogEntry(message) {
        var data = {
            "log_data": message,
            "action_type": 'create',
            "model_name": "POS Log"
        }

        fetch('/pos/logger', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        }).then(response => {
            if (!response.ok) {

            }
            return response.json();
        }).then(data => {
            // Handle successful response data
        }).catch(error => {
            // Handle errors
        });
    },
    async _processData(loadedData) {
        await super._processData(...arguments);
        this.void_reasons = loadedData["void.reason"];
        this.taxes = loadedData["account.tax"];

        // if (window.Android != undefined) {
        //     if (window.Android.isAndroidPOS()) {
        //         var result = await window.Android.getMachineData();
        //         var resObj = JSON.parse(result);

        //         var serial = resObj["serialNo"];
        //         var fiscalInfo = resObj["fiscalInfo"];
        //         var tinNo = fiscalInfo.split(",")[0];
        //         var mrc = fiscalInfo.split(",")[1];

        //         if (this.config.serial_number !== serial || this.config.fiscal_mrc !== mrc) {
        //             alert("Error: Invalid POS - Device Configuration");
        //             window.history.back();
        //         }
        //     }
        //     else {
        //         alert("Error: Invalid Device");
        //         window.history.back();
        //     }
        // } else {
        //     alert("Error: Invalid Device");
        //     window.history.back();
        // }
    },
});