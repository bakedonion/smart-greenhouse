document.addEventListener('DOMContentLoaded', function () {
    var socket = io();

    socket.on('measurements_update', function (msg, cb) {
        info_group = document.getElementById(msg.info_group);

        for (var measurement in msg.measurements) {
            info_group.querySelector(`[id^=${measurement}]`).innerText = msg.measurements[measurement];
        }
    });

    // TODO needs cleaning, right now only works for controller devices, to show what's possible
    socket.on('direct_method_response', function (msg, cb) {
        controller = msg.payload.Device;

        if (msg.status == 200 && controller.includes('Controller')) {
            status = '';

            switch (msg.payload.Method) {
                case 'turn_on':
                    status = 'on';

                    // simulate irrigation
                    if (controller.startsWith('IrrigationController')) {
                        split = controller.split('-');
                        num = split[split.length - 1];
                        url = `https://smart-greenhouse-iot-hub.azure-devices.net/twins/SoilSensorsDevice-${num}/methods?api-version=2018-06-30`;

                        socket.emit('direct_method_event', {
                            url: url,
                            method_name: 'reset_soil_humidity',
                            arguments: {}
                        });
                    }

                    break;
                case 'turn_off':
                    status = 'off';
                    break;
                case 'open':
                    status = 'open';
                    break;
                case 'close':
                    status = 'closed';
                    break;
            }

            document.getElementById(controller).innerText = status;
        }
    });

    // TODO needs cleaning, right now just to show what's possible
    document.querySelectorAll('[id*=Controller]').forEach((controller) => {
        let url = `https://smart-greenhouse-iot-hub.azure-devices.net/twins/${controller.id}/methods?api-version=2018-06-30`

        controller.addEventListener('click', function (event) {
            let method_name = '';

            switch (controller.innerHTML) {
                case 'off':
                    method_name = 'turn_on';
                    break;
                case 'on':
                    method_name = 'turn_off';
                    break;
                case 'open':
                    method_name = 'close';
                    break;
                case 'closed':
                    method_name = 'open';
                    break;
                default:
                    method_name = controller.id === 'WindowController' ? 'open' : 'turn_on';
            }

            socket.emit('direct_method_event', {
                url: url,
                method_name: method_name,
                arguments: {}
            });
        });
    });
});
