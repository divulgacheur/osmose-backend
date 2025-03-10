#!/usr/bin/env python
#-*- coding: utf-8 -*-

###########################################################################
##                                                                       ##
## Copyrights Jérôme Amagat 2019                                         ##
##                                                                       ##
## This program is free software: you can redistribute it and/or modify  ##
## it under the terms of the GNU General Public License as published by  ##
## the Free Software Foundation, either version 3 of the License, or     ##
## (at your option) any later version.                                   ##
##                                                                       ##
## This program is distributed in the hope that it will be useful,       ##
## but WITHOUT ANY WARRANTY; without even the implied warranty of        ##
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         ##
## GNU General Public License for more details.                          ##
##                                                                       ##
## You should have received a copy of the GNU General Public License     ##
## along with this program.  If not, see <http://www.gnu.org/licenses/>. ##
##                                                                       ##
###########################################################################

from modules.OsmoseTranslation import T_
from .Analyser_Merge import Analyser_Merge, SourceDataGouv, CSV, Load, Conflate, Select, Mapping
from io import open

class _Analyser_Merge_Radio_Support_FR(Analyser_Merge):
    def __init__(self, config, logger, clas, NAT_IDs, title, tags_select, tags_generate):
        Analyser_Merge.__init__(self, config, logger)
        self.def_class_missing_official(item = 8390, id = 1+10*clas, level = 3, tags = ['merge', 'fix:survey', 'fix:imagery'],
            title = T_('Radio support ({0}) not integrated', title))
        self.def_class_possible_merge(item = 8391, id = 3+10*clas, level = 3, tags = ['merge', 'fix:chair'],
            title = T_('Radio support ({0}), integration suggestion', title))
        self.def_class_update_official(item = 8392, id = 4+10*clas, level = 3, tags = ['merge', 'fix:chair'],
            title = T_('Radio support ({0}) update', title))

        self.communeNameIndexedByInsee = {}
        with open("dictionaries/FR/BddCommunes", "r", encoding="utf-8") as f:
            for x in f:
                x = x.split("\t")
                code_insee = x[0]
                name_insee = x[1].strip()
                self.communeNameIndexedByInsee[code_insee] = name_insee

        self.init(
            "https://www.data.gouv.fr/fr/datasets/donnees-sur-les-installations-radioelectriques-de-plus-de-5-watts-1/",
            "Données sur les installations radioélectriques de plus de 5 watts",
            CSV(SourceDataGouv(attribution = "data.gouv.fr:ANFR",
                    dataset = "551d4ff3c751df55da0cd89f", resource = "5da74526-7781-4726-b98b-232756643090", zip = "SUP_SUPPORT.txt", encoding = "ISO-8859-15"),
                separator = ";", quote = u'$'),
            Load(
("CASE \"COR_CD_EW_LON\" WHEN 'W' THEN -1*(to_number(\"COR_NB_DG_LON\", '99') + to_number(\"COR_NB_MN_LON\", '99') / 60 + to_number(\"COR_NB_SC_LON\", '99') / 3600) WHEN 'E' THEN to_number(\"COR_NB_DG_LON\", '99') + to_number(\"COR_NB_MN_LON\", '99') / 60 + to_number(\"COR_NB_SC_LON\", '99') / 3600 END",),
("CASE \"COR_CD_NS_LAT\" WHEN 'S' THEN -1*(to_number(\"COR_NB_DG_LAT\", '99') + to_number(\"COR_NB_MN_LAT\", '99') / 60 + to_number(\"COR_NB_SC_LAT\", '99') / 3600) WHEN 'N' THEN to_number(\"COR_NB_DG_LAT\", '99') + to_number(\"COR_NB_MN_LAT\", '99') / 60 + to_number(\"COR_NB_SC_LAT\", '99') / 3600 END",),
                select = {"NAT_ID": NAT_IDs},
                unique = ("SUP_ID",)),
            Conflate(
                select = Select(
                    types = ["nodes", "ways"],
                    tags = tags_select),
                conflationDistance = 50,
                osmRef = "ref:FR:ANFR",
                mapping = Mapping(
                    static1 = tags_generate,
                    static2 = {"source": self.source},
                    mapping1 = {
                        "ref:FR:ANFR": "SUP_ID",
                        "operator": lambda fields: self.owner[int(fields["TPO_ID"])] if fields["TPO_ID"] and int(fields["TPO_ID"]) in self.owner else None,
                        "height": lambda fields: fields["SUP_NM_HAUT"].replace(",", ".") if fields["SUP_NM_HAUT"] else None,
                    },
                    text = lambda tags, fields: {"en": "{0}, address: {1}, {2}{3}".format(
                        (lambda x: self.Tour_Mat_Pylone[fields["NAT_ID"]] if x == "Tour, mât et pylône" else x)(title),
                        ", ".join(filter(lambda x: x != "None", [fields["ADR_LB_LIEU"], fields["ADR_LB_ADD1"], fields["ADR_LB_ADD2"], fields["ADR_LB_ADD3"],fields["ADR_NM_CP"]])),
                        (lambda x: self.communeNameIndexedByInsee[x] if x in self.communeNameIndexedByInsee else x)(fields["COM_CD_INSEE"]),
                        (lambda x: (", operator: " + self.other_owner[int(x)]) if x and x != "None" and int(x) in self.other_owner else "")(fields["TPO_ID"])
                    )} )))

    # number: column TPO_ID in SUP_SUPPORT.txt and value: SUP_PROPRIETAIRE.txt
    owner = {
        1: "ANFR",
        4: "Bouygues",
        10: "CROSS",
        16: "Orange Services Fixes",
        19: "La Poste",
        21: "Orange",
        24: "SNCF Réseau",
        25: "RTE",
        27: "SFR",
        31: "Société réunionnaise du radiotéléphone",
        32: "TDF",
        33: "Towercast",
        35: "Voies navigables de France",
        36: "Altitude Telecom",
        37: "Antalis",
        38: "One Cast",
        39: "Gendarmerie nationale",
        40: "Tikiphone",
        41: "France Caraibes Mobiles",
        42: "IFW-Free",
        43: "Lagardère Active Média",
        44: "Outremer Telecom",
        45: "RATP",
        47: "Office des Postes et Telecom",
        49: "Bolloré",
        48: "Neuf Cegetel",
        50: "Completel",
        51: "Digicel",
        52: "Eutelsat",
        53: "Expertmedia",
        54: "Mediaserv",
        55: "Belgacom",
        56: "Airbus",
        57: "Guyane Numérique",
        58: "Dauphin Telecom",
        59: "Itas Tim",
        60: "Réunion Numérique",
        62: "SNCF",
        64: "Pacific Mobile Telecom",
        63: "Viti",
        61: "Globecast",
        69: "Zeop",
        68: "Cellnex",
        67: "Service des Postes et Telecom",
        65: "ATC France",
        66: "Telco OI"
    }
    other_owner = {
        2: "Association",
        3: "Aviation Civile",
        5: "CCI,Ch Metiers,Port Aut,Aérop",
        6: "Conseil Départemental",
        7: "Conseil Régional",
        8: "Coopérative Agricole, Vinicole",
        9: "Copropriété, Syndic, SCI",
        11: "DDE",
        12: "Autres",
        13: "EDF ou GDF",
        14: "Etablissement de soins",
        15: "Etat, Ministère",
        17: "Syndicat des eaux, Adduction",
        18: "Intérieur",
        20: "Météo",
        22: "Particulier",
        23: "Phares et balises",
        26: "SDIS, secours, incendie",
        28: "Société HLM",
        29: "Société Privée SA",
        30: "Sociétés d'Autoroutes",
        34: "Commune, communauté de commune",
        46: "Titulaire programme Radio/TV",
    }

    Tour_Mat_Pylone = {
        "11": "Mât béton",
        "12": "Mât métallique",
        "21": "Pylône",
        "22": "Pylône autoportant",
        "23": "Pylône autostable",
        "24": "Pylône haubané",
        "25": "Pylône treillis",
        "26": "Pylône tubulaire",
        "42": "Mât",
        "48": "pylône arbre"
    }

class Analyser_Merge_Tour_Mat_Pylone(_Analyser_Merge_Radio_Support_FR):
    def __init__(self, config, logger = None):
        _Analyser_Merge_Radio_Support_FR.__init__(self, config, logger, 0, [u'11', u'12', u'21', u'22', u'23', u'24', u'25', u'26', u'42', u'48'], "Tour, mât et pylône",
                                                  [{"man_made": "tower","tower:type": "communication"},{"man_made": "mast","tower:type": "communication"},{"man_made": "communications_tower"}],
                                                  {"man_made": "mast","tower:type": "communication"})

class Analyser_Merge_Tour_Hertzienne(_Analyser_Merge_Radio_Support_FR):
    def __init__(self, config, logger = None):
        _Analyser_Merge_Radio_Support_FR.__init__(self, config, logger, 1, u'33', "Tour hertzienne",
                                                  [{"man_made": "tower","tower:type": "communication"},{"man_made": "mast","tower:type": "communication"},{"man_made": "communications_tower"}],
                                                  {"man_made": "communications_tower"})

class Analyser_Merge_Tour_Controle(_Analyser_Merge_Radio_Support_FR):
    def __init__(self, config, logger = None):
        _Analyser_Merge_Radio_Support_FR.__init__(self, config, logger, 2, u'44', "Tour de contrôle",
                                                  {"man_made": "tower", "service": "aircraft_control"}, {"man_made": "tower", "service": "aircraft_control"})

class Analyser_Merge_Chateau_Eau(_Analyser_Merge_Radio_Support_FR):
    def __init__(self, config, logger = None):
        _Analyser_Merge_Radio_Support_FR.__init__(self, config, logger, 3, u'4', "Château d'eau ou réservoir", {"man_made": "water_tower"}, {"man_made": "water_tower"})

class Analyser_Merge_Silo(_Analyser_Merge_Radio_Support_FR):
    def __init__(self, config, logger = None):
        _Analyser_Merge_Radio_Support_FR.__init__(self, config, logger, 4, u'31', "Silo", {"man_made": "silo"}, {"man_made": "silo"})

class Analyser_Merge_Phare(_Analyser_Merge_Radio_Support_FR):
    def __init__(self, config, logger = None):
        _Analyser_Merge_Radio_Support_FR.__init__(self, config, logger, 5, u'41', "Phare", {"man_made": "lighthouse"}, {"man_made": "lighthouse"})

class Analyser_Merge_Eolienne(_Analyser_Merge_Radio_Support_FR):
    def __init__(self, config, logger = None):
        _Analyser_Merge_Radio_Support_FR.__init__(self, config, logger, 6, u'52', "Éolienne", {"power": "generator","generator:source": "wind"}, {"power": "generator","generator:source": "wind"})
