import xml.etree.ElementTree as ET
import os

class OneCMetadataTree():
    gitPath = ''
    confName = ''
    def __init__(self, gitPath, confName):
        self.gitPath = gitPath
        self.confName = confName

    def readHeadStructure(self):
        if self.gitPath != '':
            if os.path.exists(f'{self.gitPath}/Configuration.xml'):
                xmlTree = ET.parse()
                treeRoot = xmlTree.getroot()
                for child in treeRoot:
                    print(child.tag, child.attrib)      
                    """
                    Собираем по тегу в список с словарем(Аттрибут, путь), рекурсивно(вложеность неизвестна)
                    """        
            else:
                print('File not exists')

def metadataPicturesPaths(metaName: str):
    dataPictures = {"Language": "data/language.jpg",
                    "Subsystem": "data/subsystem.jpg",
                    "StyleItem": "data/styleitem.jpg",
                    "Style": "data/style.jpg",
                    "CommonPicture":"data/commonpicture.jpg",
                    "Role": "data/role.jpg",
                    "CommonTemplate": "data/commontemplate.jpg",
                    "CommonModule": "data/commonmodule.jpg",
                    "CommonAttribute": "data/commonattribute.jpg",
                    "ExchangePlan": "data/exchangeplan.jpg",
                    "XDTOPackage": "data/xdtopackage.jpg",
                    "EventSubscription": "data/eventsubscription.jpg",
                    "ScheduledJob": "data/scheduledjob.jpg",
                    "DefinedType": "data/definedtype.jpg",
                    "CommonCommand": "data/commoncommand.jpg",
                    "Constant": "data/constant.jpg",
                    "CommonForm": "data/commonform.jpg",
                    "Catalog": "data/catalog.jpg",
                    "Document": "data/document.jpg",
                    "Enum": "data/enum.jpg",
                    "Report": "data/report.jpg",
                    "DataProcessor": "data/dataprocessor.jpg",
                    "InformationRegister": "data/informationregister.jpg",
                    "AccumulationRegister": "data/accumulationregister.jpg",
                    "ChartOfCharacteristicTypes": "data/chartofcharacteristictype.jpg",
                    "SessionParameter": "data/sessionparameter.jpg",
                    "FilterCriterion": "data/filtercritereon.jpg",
                    "DocumentJournal": "data/documentjournal.jpg",
                    "BusinessProcess": "data/businessprocess.jpg",
                    "Task": "data/task.jpg",
                    "FunctionalOption": "data/functionaloption.jpg",
                    "SettingsStorage": "data/settingsstorage.jpg",
                    "CommandGroup": "data/commandgroup.jpg"}
    return dataPictures.get(metaName)
    
def metadataParentObjects(objectName: str):
    return {"Common":["Subsystem", "CommonModule", "SessionParameter", "Role", "ExchangePlan", "FilterCriterion", 
               "EventSubscription", "ScheduledJob", "FunctionalOption", "DefinedType", "SettingsStorage", 
               "CommonCommand", "CommandGroup", "CommonForm", "CommonTemplate", "CommonPicture", "XDTOPackage"],
    "Constants":["Constant"],
    "Catalogs": ["Catalog"],
    "Documents": ["Document"],
    "DocumentJournals": ["DocumentJournal"],
    "Enums": ["Enum"],
    "Reports": ["Report"],
    "DataProcessors": ["DataProcessor"],
    "ChartOfCharacteristicTypes": ["ChartOfCharacteristicTypes"],
    "InformationRegisters": ["InformationRegister"],
    "AccumulationRegisters": ["AccumulationRegister"],
    "BusinessProcesses": ["BusinessProcess"],
    "Task":["Task"]
    }
    
    
                    
        