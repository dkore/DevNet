import os
import csv
import argparse
import logging
import logging.config
from channel import channel


app="IOT-BMS Silent"
description="To Map IP's to device tracking table and bind MAC/IP/VLAN to its subsequent interface"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CSV_CONFIG_HEADERS=['switch','vlanid','ipaddress','mac','interface']
CSV_SWITCH_HEADERS=['switch','hostname','port','username','password']

logger=logging.getLogger('scriptExecutionLog')
logger_ignore_values=["password"]

def __init__():
    if not os.path.exists(os.path.join(BASE_DIR,'logs')):
        os.mkdir(os.path.join(BASE_DIR,'logs'))
    log_config=os.path.join(BASE_DIR,'config/logger.conf')
    if not os.path.exists(log_config):
        raise OSError('Unable to access {}'.format(log_config))
    logging.config.fileConfig(fname=log_config)

def welcome_message():
    from pyfiglet import Figlet

    f = Figlet(font='banner3',justify="SIDE",width=120)
    print(f.renderText(app))

def get_cmdline_arguements():
    parser = argparse.ArgumentParser(epilog=app,description=description)
    parser.add_argument("-c","--config",help="CSV with configurations",required=True)
    parser.add_argument("-d", "--devices", help="CSV with Switch Details",required=True)

    args=parser.parse_args()
    return args

def import_file(filename,headers):
    if os.path.exists(filename):
        config_data={}
        try:
            with open(filename,encoding='utf-8-sig') as csvfile:
                content=csv.reader(csvfile)
                for row in content:
                    config_data_line={}
                    if row==headers:
                        continue
                    for key,value in zip(headers,row):
                        config_data_line[key]=value
                    if config_data_line[headers[0]] in config_data.keys():
                        config_data[config_data_line[headers[0]]].append(config_data_line)
                    else:
                        config_data[config_data_line[headers[0]]]=[config_data_line]

            logger.debug('Imported file successfully {}'.format(filename))
            return config_data
        except csv.Error as csvError:
            logger.error('error occurred during import file {}'.format(csvError))
    else:
        logger.error('unable to find/access {}'.format(filename))


def execute_command(con,command):
    logger.info(command)
    response = con.sendCommand(command)
    logger.info(response)

def configure_sequence(con,conf_details):
    logger.debug('performing configuration steps ...')

    # Run bind configurations
    for detail in conf_details:
        vlan_id = detail[CSV_CONFIG_HEADERS[1]]
        ip_address = detail[CSV_CONFIG_HEADERS[2]]
        mac = detail[CSV_CONFIG_HEADERS[3]]
        interface = detail[CSV_CONFIG_HEADERS[4]]

        # For device tracking configuration
        command = 'config terminal \n' + \
                  'interface {} \n'.format(interface) + \
                  'switchport access vlan {} \n'.format(vlan_id) + \
                  'switchport mode access \n' + \
                  'device-tracking attach-policy IPDT_MAX_10 \n' + \
                  'access-session control-direction in \n' + \
                  'dot1x timeout tx-period 7 \n' + \
                  'dot1x max-reauth-req 3 \n' + \
                  'source template DefaultWiredDot1xClosedAuth \n'+ \
                  'spanning-tree portfast \n' + \
                  'end\n'
        execute_command(con, command)

        # Before binding
        command = 'show device-tracking database interface {} \n'.format(interface)
        execute_command(con, command)

        # Binding
        command = 'config terminal \n' + \
                  'arp vrf BACKBONE_VN {} {} ARPA \n'.format(ip_address,mac) + \
                  'device-tracking binding vlan {} {} interface {} {} \n'.format(vlan_id,ip_address,interface,mac) +\
                  'end\n'
        execute_command(con, command)

        # After Binding
        command = 'show device-tracking database interface {} \n'.format(interface)
        execute_command(con, command)

    # Copying Running Config to startup
    command = 'copy running-config startup-config \n'
    execute_command(con, command)

    # exit connection
    command = 'exit'
    execute_command(con, command)

def apply_configuration(switch_data,conf_data):
    for switch in switch_data.keys():
        details=switch_data[switch]
        chosen=details[-1]
        con=None

        try:
            address = chosen[CSV_SWITCH_HEADERS[1]]
            port = None
            if not chosen[CSV_SWITCH_HEADERS[2]] == '':
                port = chosen[CSV_SWITCH_HEADERS[2]]
            username = chosen[CSV_SWITCH_HEADERS[3]]
            password = chosen[CSV_SWITCH_HEADERS[4]]

            for conf in conf_data.keys():
                if switch == conf:
                    conf_details = conf_data[conf]
                    switch_details=dict(filter(lambda elem: elem[0] not in logger_ignore_values, chosen.items()))
                    logger.debug(
                        'switch details - ({})'.format(switch_details))

                    logger_file_name = "_".join(['device',switch,address])
                    custom_logger = logging.handlers.TimedRotatingFileHandler(os.path.join(BASE_DIR,'logs','{}.log'.format(logger_file_name)), 'midnight')
                    custom_formatter= logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s')

                    custom_logger.setFormatter(custom_formatter)
                    logger.addHandler(custom_logger)
                    # Register custom device logger for seperate logging
                    try:
                        logger.info('Connecting to {} - {}'.format(switch,address))
                        con = channel(address=address, port=port, username=username, password=password)
                        configure_sequence(con,conf_details)
                    except Exception as err:
                        logger.error(err)

                    # Unregister custom logger to stop further logging
                    logger.removeHandler(custom_logger)

        except Exception as err:
            logger.error(err)
        finally:
            if con:
                con.closeSession()


if __name__=="__main__":
    welcome_message()
    args=get_cmdline_arguements()

    __init__()
    conf_data=import_file(args.config,CSV_CONFIG_HEADERS)
    switch_data=import_file(args.devices,CSV_SWITCH_HEADERS)
    apply_configuration(switch_data,conf_data)
