# -*- coding: utf-8 -*-

import json

# target_device = ['bms','pcs--ess']
# target_value = {'bms':['802','1803'],'pcs--ess':['113'] }
# target_id = {'802':['A','AChaMax','ADisChaMax','SoC','SoH','V'], '1803':['VCell','VCellMax','VCellMin'], '113':['DCA','DCV','DCW','VAr','W']}

# kwargs.keys()[k]) + str(kwargs.values()[k][l + 1])

# target_device=['bms','pcs--ess']
# target_value_b=[['802','1803'],['113']]
# c =[['A','AChaMax','ADisChaMax','SoC','SoH','V'],['VCell','VCellMax','VCellMin'],['DCA','DCV','DCW','VAr','W']]
#
#
# target_value={}
# kk={}
# i=0
# k=0
# # bms, pcs--ess
# for device in target_device:
#     # print("--------------")
#     # print("device: ",device)
#     tt = {}
#
#     # b 2번
#     for device2 in target_value_b[i]:
#         # print("device2: ",device2)
#         target_value2 = {}
#         tt[device2]=c[k]
#         # print("tt: ",tt)
#         k+=1
#
#     kk[device] = tt
#     target_value.update(kk)
#     i+=1


# print(target_value)
# ttt=['802','1803','113']
# print(target_value.pop('bms'))
#
# print(range(len(target_value.keys())))

input_value =  {'bms': {'802': ['A', 'AChaMax', 'ADisChaMax', 'SoC', 'SoH', 'V'], '1803': ['VCell', 'VCellMax', 'VCellMin']},
                'pcs--ess': {'113': ['DCA', 'DCV', 'DCW', 'VAr', 'W']}}
# target_device = ['bms','pcs--ess']
# target_value = {'bms':['802','1803'],'pcs--ess':['113'] }
# target_id = {'802':['A','AChaMax','ADisChaMax','SoC','SoH','V'], '1803':['VCell','VCellMax','VCellMin'], '113':['DCA','DCV','DCW','VAr','W']}
#             {'113': ['DCA', 'DCV', 'DCW', 'VAr', 'W'], '802': ['A', 'AChaMax', 'ADisChaMax', 'SoC', 'SoH', 'V'], '1803': ['VCell', 'VCellMax', 'VCellMin']}
# def make_list(input_value):
#     target_device = []
#     target_id = {}
#     target_value = {}
#
#     for t_device in input_value.keys():
#         target_device.append(t_device)
#         t_value = input_value.get(t_device)
#         target_id.update(t_value)
#         target_id_key_value = {}
#         target_id_key = []
#
#         for t_id in t_value.keys():
#             target_id_key.append(t_id)
#             target_id_key_value[t_device]=target_id_key
#             target_value.update(target_id_key_value)
#
#     return target_device, target_value, target_id
#
# a, b, c = make_list(input_value)
#
# print(a, b, c)

# target_value={}
#
# kk={}
# i=0
# # bms, pcs--ess
# for device in target_device:
#     kk[device]=target_value_b[i]
#     target_value.update(kk)
#     i+=1
#
# print(target_value)


# target_value2={}
#
# tt={}
# j=0
# for device2 in c:
#     k=0
#     target_value3 = {}
#     for device3 in target_value_b:
#         # "802"=aaaa, "1803"=bbbb
#         for device4 in device3:
#             tt[device4] = device2[j]
#             target_value3.update(tt)

# target_value = {'bms':['802','1803'],'pcs--ess':['113'] }
test_value1 = {
    "bms": {
        "802": {
            "A": 0,
            "AChaMax": 541.2,
            "ADisChaMax": 244.7,
            "EvtVnd1": [],
            "EvtVnd2": [],
            "EvtVnd3": [],
            "EvtVnd4": [],
            "SoC": 5,
            "SoH": 97.5,
            "StEvtVnd": {
                "charge status": "IDLE",
                "comm error": "NORMAL",
                "contactor control": "NORMAL",
                "fault": "NORMAL",
                "high soc alram": "NORMAL",
                "low soc alram": "NORMAL",
                "online": "ONLINE",
                "under balance": "NORMAL",
                "warning": "NORMAL"
            },
            "StVnd": "NORMAL",
            "V": 820.3,
            "WChaMax": 444000,
            "WDisChaMax": 200800
        },
        "1803": {
            "Tmp": 22,
            "TmpMax": 24.5,
            "TmpMin": 17,
            "TmpMinMaxLoc": {
                "max": 2,
                "min": 2
            },
            "VCell": 3.446,
            "VCellMax": 3.465,
            "VCellMin": 3.41,
            "VCellMinMaxLoc": {
                "max": 2,
                "min": 1
            }
        },
        "1805": {
            "Hb": 0,
            "NRack": 4,
            "NRackCellBal": 0,
            "NRackDsOn": 4,
            "NRackFanOn": 0,
            "NRackFault": 0,
            "NRackOn": 4,
            "NRackWarn": 0
        },
        "1823": {
            "Bsc": 0,
            "Contactor": "NONE",
            "Hb": 0,
            "ManMode": 0,
            "Rst": "NONE",
            "Sleep": 0,
            "StController": "SHUTDOWN"
        },
        "1825": {}
    },
    "meter--ess": {
        "214": {
            "A": 0,
            "AphA": 0,
            "AphB": 0,
            "AphC": 0,
            "Hz": 0,
            "PF": 0,
            "PPVphAB": 0,
            "PPVphBC": 0,
            "PPVphCA": 0,
            "PhV": 0,
            "PhVphA": 0,
            "PhVphB": 0,
            "PhVphC": 0,
            "TotVAhImp": 0,
            "TotWhExp": 0,
            "TotWhImp": 0,
            "VA": 0,
            "VAR": 0,
            "VARphA": 0,
            "VARphB": 0,
            "VARphC": 0,
            "VAphA": 0,
            "VAphB": 0,
            "VAphC": 0,
            "W": 0,
            "WphA": 0,
            "WphB": 0,
            "WphC": 0
        }
    },
    "meter--grid": {
        "214": {
            "AphA": 0,
            "AphB": 0,
            "AphC": 0,
            "Hz": 0,
            "PF": 0,
            "PPVphAB": 0,
            "PPVphBC": 0,
            "PPVphCA": 0,
            "PhVphA": 0,
            "PhVphB": 0,
            "PhVphC": 0,
            "TotVAhImp": 0,
            "TotWhExp": 0,
            "TotWhImp": 0,
            "VAR": 0,
            "W": 0
        }
    },
    "meter--load": {},
    "meter--pv": {
        "214": {
            "A": 0,
            "AphA": 0,
            "AphB": 0,
            "AphC": 0,
            "Hz": 60.01651,
            "PF": 0,
            "PPVphAB": 385.35727,
            "PPVphBC": 385.22623,
            "PPVphCA": 383.4875,
            "PhV": 222.12413,
            "PhVphA": 222.05371,
            "PhVphB": 222.7572,
            "PhVphC": 221.56148,
            "TotVAhImp": 137521260,
            "TotWhExp": 0,
            "TotWhImp": 136852060,
            "VA": 0,
            "VAR": 0,
            "VARphA": 0,
            "VARphB": 0,
            "VARphC": 0,
            "VAphA": 0,
            "VAphB": 0,
            "VAphC": 0,
            "W": 0,
            "WphA": 0,
            "WphB": 0,
            "WphC": 0
        }
    },
    "pcs--ess": {
        "113": {
            "AphA": 7.6,
            "AphB": 7.6,
            "AphC": 7.7,
            "DCA": 0.3,
            "DCV": 821,
            "DCW": 200,
            "Evt1": [],
            "EvtVnd1": [],
            "EvtVnd2": [],
            "EvtVnd3": [],
            "EvtVnd4": [],
            "Hz": 60.138,
            "PF": 0.02,
            "PPVphAB": 441.1,
            "PPVphBC": 440.5,
            "PPVphCA": 446.2,
            "StVnd": "Stand-by",
            "TmpCab": 21,
            "TmpSnk": 27,
            "VAr": 5700,
            "W": 0
        },
        "123": {
            "Conn": "CONNECT"
        },
        "1113": {
            "AphA": 8.8,
            "AphB": 8.7,
            "AphC": 8.7,
            "DCV": 820.3,
            "Hz": 60.134,
            "PPVphAB": 382,
            "PPVphBC": 384,
            "PPVphCA": 383.4,
            "StPcsVnd1": [
                "CB1 ON",
                "MC4 ON",
                "CB3 ON",
                "",
                "",
                "System On"
            ],
            "WHCha": 134198492.8,
            "WHDisCha": 115206648
        },
        "1123": {
            "VarRem": 0,
            "WRem": 0
        },
        "001": {
            "Vr": {
                "param": 1003,
                "sw": 10001
            }
        }
    },
    "pcs--pv": {},
    "pms": {
        "1020": {
            "StCommVnd": {
                "bms": True,
                "meter--ess": False,
                "meter--grid": False,
                "meter--pv": True,
                "pcs--ess": True
            }
        }
    },
    "racks": {
        "0": {
            "802": {
                "A": 0,
                "AChaMax": 148.4,
                "ADisChaMax": 69.6,
                "EvtVnd1": [],
                "EvtVnd3": [],
                "SoC": 5,
                "SoH": 97.5,
                "StEvtVnd": {
                    "bpu fan feedback": "OFF",
                    "cell balancing": "NORMAL",
                    "charge status": "IDLE",
                    "disconnect switch feedback": "ON",
                    "every mbms turned on": "ON",
                    "fan status": "OFF",
                    "fault": "NORMAL",
                    "high soc alram": "NORMAL",
                    "low soc alram": "NORMAL",
                    "main contactor   feedback": "ON",
                    "main contactor   status": "ON",
                    "main contactor - feedback": "ON",
                    "main contactor - status": "ON",
                    "module fan feedback": "OFF",
                    "online": "ONLINE",
                    "precharge contactor status": "OFF",
                    "warning": "NORMAL"
                },
                "StVnd": "NORMAL",
                "V": 820.3,
                "W": 0,
                "WChaMax": 121800,
                "WDisChaMax": 57100
            },
            "1803": {
                "Tmp": 22.5,
                "TmpMax": 24,
                "TmpMin": 18,
                "TmpMinMaxLoc": {
                    "max": 32,
                    "min": 2
                },
                "VCell": 3.446,
                "VCellMax": 3.463,
                "VCellMin": 3.41,
                "VCellMinMaxLoc": {
                    "max": 1,
                    "min": 234
                }
            },
            "1805": {
                "NModOn": 65535
            }
        },
        "1": {
            "802": {
                "A": 0,
                "AChaMax": 148.4,
                "ADisChaMax": 61.1,
                "EvtVnd1": [],
                "EvtVnd3": [],
                "SoC": 5,
                "SoH": 98,
                "StEvtVnd": {
                    "bpu fan feedback": "OFF",
                    "cell balancing": "NORMAL",
                    "charge status": "IDLE",
                    "disconnect switch feedback": "ON",
                    "every mbms turned on": "ON",
                    "fan status": "OFF",
                    "fault": "NORMAL",
                    "high soc alram": "NORMAL",
                    "low soc alram": "NORMAL",
                    "main contactor   feedback": "ON",
                    "main contactor   status": "ON",
                    "main contactor - feedback": "ON",
                    "main contactor - status": "ON",
                    "module fan feedback": "OFF",
                    "online": "ONLINE",
                    "precharge contactor status": "OFF",
                    "warning": "NORMAL"
                },
                "StVnd": "NORMAL",
                "V": 820.4,
                "W": 0,
                "WChaMax": 121800,
                "WDisChaMax": 50200
            },
            "1803": {
                "Tmp": 22.5,
                "TmpMax": 24.5,
                "TmpMin": 17,
                "TmpMinMaxLoc": {
                    "max": 29,
                    "min": 2
                },
                "VCell": 3.447,
                "VCellMax": 3.465,
                "VCellMin": 3.407,
                "VCellMinMaxLoc": {
                    "max": 226,
                    "min": 152
                }
            },
            "1805": {
                "NModOn": 65535
            }
        },
        "2": {
            "802": {
                "A": 0,
                "AChaMax": 148.4,
                "ADisChaMax": 69.6,
                "EvtVnd1": [],
                "EvtVnd3": [],
                "SoC": 5,
                "SoH": 98,
                "StEvtVnd": {
                    "bpu fan feedback": "OFF",
                    "cell balancing": "NORMAL",
                    "charge status": "IDLE",
                    "disconnect switch feedback": "ON",
                    "every mbms turned on": "ON",
                    "fan status": "OFF",
                    "fault": "NORMAL",
                    "high soc alram": "NORMAL",
                    "low soc alram": "NORMAL",
                    "main contactor   feedback": "ON",
                    "main contactor   status": "ON",
                    "main contactor - feedback": "ON",
                    "main contactor - status": "ON",
                    "module fan feedback": "OFF",
                    "online": "ONLINE",
                    "precharge contactor status": "OFF",
                    "warning": "NORMAL"
                },
                "StVnd": "NORMAL",
                "V": 820.4,
                "W": 0,
                "WChaMax": 121800,
                "WDisChaMax": 57100
            },
            "1803": {
                "Tmp": 22.5,
                "TmpMax": 24,
                "TmpMin": 18,
                "TmpMinMaxLoc": {
                    "max": 32,
                    "min": 1
                },
                "VCell": 3.447,
                "VCellMax": 3.461,
                "VCellMin": 3.41,
                "VCellMinMaxLoc": {
                    "max": 1,
                    "min": 123
                }
            },
            "1805": {
                "NModOn": 65535
            }
        },
        "3": {
            "802": {
                "A": 0,
                "AChaMax": 148.4,
                "ADisChaMax": 69.6,
                "EvtVnd1": [],
                "EvtVnd3": [],
                "SoC": 5,
                "SoH": 98,
                "StEvtVnd": {
                    "bpu fan feedback": "OFF",
                    "cell balancing": "NORMAL",
                    "charge status": "IDLE",
                    "disconnect switch feedback": "ON",
                    "every mbms turned on": "ON",
                    "fan status": "OFF",
                    "fault": "NORMAL",
                    "high soc alram": "NORMAL",
                    "low soc alram": "NORMAL",
                    "main contactor   feedback": "ON",
                    "main contactor   status": "ON",
                    "main contactor - feedback": "ON",
                    "main contactor - status": "ON",
                    "module fan feedback": "OFF",
                    "online": "ONLINE",
                    "precharge contactor status": "OFF",
                    "warning": "NORMAL"
                },
                "StVnd": "NORMAL",
                "V": 820.4,
                "W": 0,
                "WChaMax": 121800,
                "WDisChaMax": 57100
            },
            "1803": {
                "Tmp": 21.5,
                "TmpMax": 23,
                "TmpMin": 18.5,
                "TmpMinMaxLoc": {
                    "max": 30,
                    "min": 2
                },
                "VCell": 3.447,
                "VCellMax": 3.462,
                "VCellMin": 3.423,
                "VCellMinMaxLoc": {
                    "max": 2,
                    "min": 238
                }
            },
            "1805": {
                "NModOn": 65535
            }
        }
    },
    "stamp": "2019-01-01T00:00:00 09:00"
}

test_value = {
    "bms": {
        "802": [
            "A",
            "AChaMax",
            "ADisChaMax",
            "SoC",
            "SoH",
            "V",
            "WChaMax",
            "WDisChaMax"
        ],
        "1803": [
            "Tmp",
            "TmpMax",
            "TmpMin",
            {"TmpMinMaxLoc": [
                "max",
                "min"
            ]},
            "VCell",
            "VCellMax",
            "VCellMin",
            {"VCellMinMaxLoc": [
                "max",
                "min"
            ]}
        ],
        "1805": [
            "Hb",
            "NRack",
            "NRackCellBal",
            "NRackDsOn",
            "NRackFanOn",
            "NRackFault",
            "NRackOn",
            "NRackWarn"
        ],
        "1823": [
            "Bsc",
            "Hb",
            "ManMode",
            "Sleep",
        ],
        "1825": {}
    },
    "meter--ess": {
        "214": [
            "A",
            "AphA",
            "AphB",
            "AphC",
            "Hz",
            "PF",
            "PPVphAB",
            "PPVphBC",
            "PPVphCA",
            "PhV",
            "PhVphA",
            "PhVphB",
            "PhVphC",
            "TotVAhImp",
            "TotWhExp",
            "TotWhImp",
            "VA",
            "VAR",
            "VARphA",
            "VARphB",
            "VARphC",
            "VAphA",
            "VAphB",
            "VAphC",
            "W",
            "WphA",
            "WphB",
            "WphC"
        ]
    },
    "meter--grid": {
        "214": [
            "AphA",
            "AphB",
            "AphC",
            "Hz",
            "PF",
            "PPVphAB",
            "PPVphBC",
            "PPVphCA",
            "PhVphA",
            "PhVphB",
            "PhVphC",
            "TotVAhImp",
            "TotWhExp",
            "TotWhImp",
            "VAR",
            "W"
        ]
    },
    "meter--load": {},
    "meter--pv": {
        "214": [
            "A",
            "AphA",
            "AphB",
            "AphC",
            "Hz",
            "PF",
            "PPVphAB",
            "PPVphBC",
            "PPVphCA",
            "PhV",
            "PhVphA",
            "PhVphB",
            "PhVphC",
            "TotVAhImp",
            "TotWhExp",
            "TotWhImp",
            "VA",
            "VAR",
            "VARphA",
            "VARphB",
            "VARphC",
            "VAphA",
            "VAphB",
            "VAphC",
            "W",
            "WphA",
            "WphB",
            "WphC"
        ]
    },
    "pcs--ess": {
        "113": [
            "AphA",
            "AphB",
            "AphC",
            "DCA",
            "DCV",
            "DCW",
            "Hz",
            "PF",
            "PPVphAB",
            "PPVphBC",
            "PPVphCA",
            "TmpCab",
            "TmpSnk",
            "VAr",
            "W"
        ],
        "123": [
            "Conn"
        ],
        "1113": [
            "AphA",
            "AphB",
            "AphC",
            "DCV",
            "Hz",
            "PPVphAB",
            "PPVphBC",
            "PPVphCA",
            "WHCha",
            "WHDisCha"
        ],
        "1123": [
            "VarRem",
            "WRem"
        ],
        "001": {
            "Vr": [
                "param",
                "sw"
            ]
        }
    },
    "pcs--pv": {},
    "pms": {
        "1020": {
        }
    },
    "racks": {
        "0": {
            "802": [
                "A",
                "AChaMax",
                "ADisChaMax",
                "EvtVnd1",
                "EvtVnd3",
                "SoC",
                "SoH",
                "V",
                "W",
                "WChaMax",
                "WDisChaMax"
            ],
            "1803": [
                "Tmp",
                "TmpMax",
                "TmpMin",
                {"TmpMinMaxLoc": [
                    "max",
                    "min"
                ]},
                "VCell",
                "VCellMax",
                "VCellMin",
                {"VCellMinMaxLoc": [
                    "max",
                    "min"
                ]}
            ],
            "1805": [
                "NModOn"
            ]
        },
        "1": {
            "802": [
                "A",
                "AChaMax",
                "ADisChaMax",
                "EvtVnd1",
                "EvtVnd3",
                "SoC",
                "V",
                "W",
                "WChaMax",
                "WDisChaMax"
            ],
            "1803": [
                "Tmp",
                "TmpMax",
                "TmpMin",
                {"TmpMinMaxLoc": [
                    "max",
                    "min"
                ]},
                "VCell",
                "VCellMax",
                "VCellMin",
                {"VCellMinMaxLoc": [
                    "max",
                    "min"
                ]}
            ],
            "1805": [
                "NModOn"
            ]
        }
    }
}



def depth(json_v):
    json_v = str(json_v)
    count_in = 0
    depth = 0
    for i in range(len(json_v)):
        if json_v[i] == '{':
            count_in += 1
        if json_v[i] == '}':
            count_in -= 1
        if depth < count_in:
            depth = count_in
    return depth

print(depth(test_value1))
'''
전체 values 에서 1-key 찾음.
찾은 1-key의 1-values의 <깊이를 구함>.

1-values에서 2-key 찾음.
찾은 2-key의 2-values 구함,
2-vslues에서 3-key 찾음.
찾은 3-key의 3-values 구함.
3-values에서 4-key ..... 
(1-value의 <깊이만큼 반복>)
'''

def search_values_name(key2_value, key):
    depth1 = []
    result_list =[]
    key_name_list = []
    key_name_list_split = []

    # if not depth(key2_value) == 1:
    if type(key2_value) is dict:
        for key3 in sorted(key2_value.keys()):
            key_name = str()
            # print("key: ",key3)
            # print("-------------------------------")
            # todo: list이름을 추가.
            key3_value = key2_value.get(key3)
            key_name += str(key)+'_'+str(key3)
            # print("key_name: ",key_name)
            # print("key3: ", key2)
            # print("key3_v: ", key2_value)

            result, depthv, aa = search_values_name(key3_value, key_name)
            # print("aa: ", aa)
            if result:
                    # result_list.append(result)
                    result_list = result_list + result
            if depthv:
                depth1.append(depthv)
            # key_name_list.append(aa)
            key_name_list = key_name_list + aa
    else:
        if key2_value:
            print(key)
            result_list = result_list + [key2_value]
            # key_name_list.append(key)
            print("vvvvvvvv: ",key2_value)

            for i in key2_value:
                if type(i) is dict:
                    for skey in sorted(i.keys()):
                        dicv = i.get(skey)
                        for k in dicv:
                            key_name_f = str(key) + '_' + str(skey)+ '_'+ str(k)
                            key_name_list = key_name_list + [key_name_f]
                else:
                    key_name_f = str(key) + '_' + str(i)
                    key_name_list = key_name_list + [key_name_f]


            # print("else_key2v", key2_value)
            # print(key_name_list_f)
    return result_list, depth1, key_name_list

# -----------------------------------------------------------
import pandas as pd
jfile = '/home/uk/PredictionServer/prediction2/JSONparser/32/2018/12/backup_2018-12-17'

# with open(jfile) as json_file:
#     jsonString = json.dumps(json_file)
#     data = json.loads(jsonString)
#     print(data)

result_depth1 = []
result_list = []
keyname_list= []
keyall = str()
for key1 in sorted(test_value.keys()):
    # print("key1: ",key1)
    # print("=========================")
    # print("income: ",test_value)
    # print("key1: ", key1)
    key1_value = test_value.get(key1)
    # print("key1name: ", key1)
    # print("key1_value: ",key1_value)
    result, depth1, keyname = search_values_name(key1_value, key1)
    # depth1, keyname = search_values_name(key1_value, key1)
    if result:
            # result_list.append(result)
            result_list = result_list + result

    if depth1:
        result_depth1.append(depth1)

    if keyname:
        keyname_list = keyname_list + keyname

    # if type(key1_value) is dict:
    #     for key2 in sorted(key1_value.keys()):
    #         key2_value = key1_value.get(key2)
    #         # print("key2: ", key2)
    #         # print("key2_v: ", key2_value)
    #
    #         # result = search_values(key2_value)
    #         # result_list.append(result)
    #
    #         # if type(key2_value) is dict:
    #         #     for key3 in sorted(key2_value.keys()):
    #         #         key3_value = key2_value.get(key3)
    #         #         print("key3: ", key2)
    #         #         print("key3_v: ", key2_value)
    #         # else:
    #         #     print("else_key2v", key2_value)
    #
    # else:
    #     print("else_key1v", key1_value)

# print(result_list)
print(keyname_list)

list_ff = []
for i in keyname_list:
    list_ff.append(i.split("_"))

print(list_ff)


data = pd.read_csv(jfile, names=['bms', 'timestamp'])
df = pd.DataFrame(data)

for json_raw in range(50):
    json_data = pd.read_json(df['bms'].iloc[json_raw])
    testtarget = json_data['bms'].loc[int(802)]['A']

    print(testtarget)
#
# final_result = []
# for json_raw in range(50):
#     json_data = pd.read_json(df['bms'].iloc[json_raw])  # json_data : pandas format
#
#     value_in=[]
#     for i in list_ff:
#         print(i)
#         try:
#
#             if len(i) == 2:
#                 testtarget = json_data[i[0]].loc[int(i[1])]
#             elif len(i) == 3:
#                 testtarget = json_data[i[0]].loc[int(i[1])][i[2]]
#             elif len(i) == 4:
#                 testtarget = json_data[i[0]].loc[int(i[1])][i[2]][i[3]]
#             elif len(i) == 5:
#                 testtarget = json_data[i[0]].loc[int(i[1])][i[2]][i[3]][i[4]]
#             elif len(i) == 6:
#                 testtarget = json_data[i[0]].loc[int(i[1])][i[2]][i[3]][i[4]][i[5]]
#             elif len(i) == 7:
#                 testtarget = json_data[i[0]].loc[int(i[1])][i[2]][i[3]][i[4]][i[5]][i[6]]
#             else:
#                 pass
#
#             value_get_str = str()
#             for value_get in i:
#                 if value_get == i[-1]:
#                     value_get_str += str(value_get)
#                 else:
#                     value_get_str += str(value_get)+'_'
#
#             final_result.append(value_get_str)
#         except Exception as e:
#             print("SKIP ERROR VALUE")
#             print(e)
#             pass
#
# print(final_result)
    # testtarget = json_data['pcs--ess'].loc[1113]
    # testtarget = testtarget['WHCha']






#     key1, key1_value, fval = search_values(key1_value)
#     print(type(key1_value))
# print('------------------------')
# print(key1_value)

# print(depth(test_value.get(key1_value)))
# for key2_value in sorted(test_value.get(key1)):
#     pass
# print("key2_value: ",key2_value)


# def set_value(input_value):
#     target_device = []
#     target_id = {}
#     target_value = {}
#
#     for t_device in sorted(input_value.keys()):
#         # target_device
#         target_device.append(t_device)
#         # target_id
#         t_value = input_value.get(t_device)
#         target_id.update(t_value)
#         target_id_key_value = {}
#         target_id_key = []
#
#         for t_id in sorted(t_value.keys()):
#             target_id_key.append(t_id)
#             target_id_key_value[t_device]=target_id_key
#             # target_value
#             target_value.update(target_id_key_value)
#
#     return target_device, target_value, target_id


# a, b, c = set_value(target_id)

# target_device = ['bms','pcs--ess']
# target_value = {'bms':['802','1803'],'pcs--ess':['113'] }
# target_id = {'802':['A','AChaMax','ADisChaMax','SoC','SoH','V'], '1803':['VCell','VCellMax','VCellMin'], '113':['DCA','DCV','DCW','VAr','W']}
#             {'113': ['DCA', 'DCV', 'DCW', 'VAr', 'W'], '802': ['A', 'AChaMax', 'ADisChaMax', 'SoC', 'SoH', 'V'], '1803': ['VCell', 'VCellMax', 'VCellMin']}
# print(a, b, c)


