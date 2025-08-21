import subprocess
import logging

ONE_C_EXE_PATH = "C:/Program Files/1cv8/common/1cestart.exe"
EXTENSION_NAME = "УВМ"
class One1C():
    def __init__(self, server: str, database: str, username: str, password: str, save_cf_path = "", load_xml_path = "") -> None:
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.save_cf_path = save_cf_path
        self.load_xml_path = load_xml_path
        logging.basicConfig(level=logging.INFO, filename="1cClassLog.log", filemode="w",
                            format="%(asctime)s %(levelname)s %(message)s")
        logging.info(f'class inited {self.server}, {self.database}')
    
    def __str__(self) -> str:
        return (f'Экземпляр класса 1C База {self.database}, сервер {self.server}')
        
    def save_to_cf(self, path_to_save: str) -> None:
        process = subprocess.run([ONE_C_EXE_PATH, 'DESIGNER', f'/IBName {self.database}', f'/N {self.username}', f'/P {self.password}', f'/DumpCfg {path_to_save}'], capture_output=True)
        if process.returncode != 0:
            self.log_process_error(process, "Ошибка при сохранении конфигурации")
    
    
    def load_from_xml(self, path_to_load: str):
        process = subprocess.run([ONE_C_EXE_PATH, 'DESIGNER', f'/IBName {self.database}', f'/N {self.username}', f'/P {self.password}', f'/LoadConfigFromFiles {path_to_load}', f'-Extension {EXTENSION_NAME}',
                                  'updateConfigDumpInfo', 'SessionTerminate force', '-v2'], capture_output=True)
        #/LoadConfigFromFiles C:\Git\ConfigFiles\ -Extension "УниверсальныеИнструменты" -updateConfigDumpInfo -SessionTerminate force -v2
        if process.returncode != 0:
            self.log_process_error(process, "Ошибка при загрузке конфигурации из XML")
    
    def kill_opened_processes(self) -> None:
        process = subprocess.run(['TASKKILL', '/F', '/IM', '1cv8.exe'], capture_output=True)
        if process.returncode != 0:
            self.log_process_error(process, "Ошибка при завершении открытых 1C")
    
    def log_process_error(self, process: subprocess.CompletedProcess, errorText: str) -> None:
        if process.stderr:
            logging.error(f'{errorText}: {process.stderr}')
        else:
            logging.error(f'{errorText} \n Неизвестная ошибка')