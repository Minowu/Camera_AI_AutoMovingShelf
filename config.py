# File: config.py
# Configuration file for constants

API_SERVER_HOST = "192.168.1.17"
API_SERVER_PORT = 5001
API_LOG_LEVEL = "info"

THRESHOLD_DETECT = 0.4
THRESHOLD_COVERAGE = 0.5

ICS_URL = "http://192.168.1.100:7000/ics/taskOrder/addTask"  # Replace with actual URL
PROCESSING_LOOP_DELAY = 1  # seconds

# Snapshot configuration
ENABLE_SNAPSHOTS = True
SNAPSHOT_DIR = "snapshots"
SNAPSHOT_QUALITY = 95  # JPEG quality (0-100)

USE_GPU_DECODE = True
GPU_DECODE_BUFFER_SIZE = 10**6  # 1MB buffer for subprocess pipe
FFMPEG_RECONNECT_DELAY = 1.0    # seconds
FFMPEG_MAX_RETRIES = 5

INFERENCE_MAX_QUEUE_SIZE = 500
INFERENCE_MAX_BATCH_SIZE = 1
INFERENCE_BATCH_TIMEOUT = 0.1
INFERENCE_NUM_STREAMS = 3
GPU_DEVICE_IDS = [0, 1]
# MODEL_PATH = "models/ModelHNAE_12022601.engine"
MODEL_PATH = "models/ModelHN_170926.engine"
CAMERA_AUTO_START = True

END_POINT_EMPTY = "end_10001546"



# Pairs theo vùng để GUI hiển thị 2 cột (AE | AF)
# ===========AE point=============
PAIRS_AE_5 = [
    # AE5
    ("start_10000060", "end_10000760"),
    ("start_10000059", "end_10000761"),
    ("start_10001050", "end_10000759"),
    ("start_10001051", "end_10000385"),
    ("start_10001052", "end_10000382"),
    ("start_10001053", "end_10000376"),
    ("start_10001054", "end_10000373"),
    ("start_10001055", "end_10000367"),
    ("start_10001056", "end_10000394"),
    ("start_10001057", "end_10000370"),
    
    # xe chuyên dụng
    ("start_10002235", "end_10000396"),
    ("start_10002232", "end_10001943"),
    ("start_10002233", "end_10000361"),
    ("start_10001762", "end_10001495"),
    ("start_10001763", "end_10000379"),

    ### Xe trống AE5
    ("start_10000391",),
    ("start_10001287",),
    ("start_10001290",),
    ("start_10001555",),
    ("start_10001295",),
    ("start_10001299",),
    ("start_10001498",),

    

    ("start_10001384", "end_10000044"),
    ("start_10001384", "end_10000045"),
    ("start_10001384", "end_10000046"),
    ("start_10001384", "end_10000047"),

    ("start_10001385", "end_10000044"),
    ("start_10001385", "end_10000045"),
    ("start_10001385", "end_10000046"),
    ("start_10001385", "end_10000047"),

    ("start_10001386", "end_10000044"),
    ("start_10001386", "end_10000045"),
    ("start_10001386", "end_10000046"),
    ("start_10001386", "end_10000047")
]

PAIRS_AE_6 = [
    #------------------ AE6 point ------------------
    ("start_10000037", "end_10000276"),
    ("start_10000038", "end_10000282"),
    ("start_10000039", "end_10000280"),
    ("start_10000040", "end_10000274"),
    ("start_10000041", "end_10000286"),
    ("start_10000042", "end_10000288"),
    ("start_10000989", "end_10000757"),
    ("start_10000992", "end_10000758"),
    

    # xe chuyên dụng
    ("start_10000063", "end_10000268"),
    ("start_10000749", "end_10000266"),
    ("start_10000748", "end_10000272"), # unused
    ("start_10000747", "end_10000267"),
    ("start_10000746", "end_10001797"), #cd5
    ("start_10002274", "end_10000290"),
    ("start_10002273", "end_10001796"), #cd7
    ("start_10002272", "end_10001793"), #cd8

   

    #### Xe trống AE6
    #("start_10000910", "end_10001386"),
    #("start_10000907", "end_10001386"),
    # ("start_10000484", "end_10001386"), #AE6-XT5
    # ("start_10000481", "end_10001386"), #AE6-XT6
    #("start_10000478", "end_10001386"), #AE6-XT7 
    ("start_10000903",), #AE6-XT3
    ("start_10000898",), #XT-moi1
    ("start_10002278",), #XT-moi2
    ("start_10002276",) #XT-moi3
]


PAIRS_SUB_5 = [
 
    ("start_10002091", "end_10001489"), #
    ("start_10002088", "end_10001488"), #
    ("start_10002086", "end_10001493"), #c44-2
    ("start_10002393", "end_10001343"), #c45-3
    ("start_10002082", "end_10001341") #c46-1 change from end 1344 to 1341
   
]


PAIR_AF = [
#------------------ AF point ------------------
    ("start_10000723", "end_10000130"),
    ("start_10000722", "end_10000600"),
    ("start_10000721", "end_10000188"),
    ("start_10001978", "end_10000612"),
    ("start_10000707", "end_10000614"),
    # ("start_10001973", "end_10002260"),
    ("start_10001975", "end_10002260"),


    # AF6
    ("start_10000727", "end_10000762"),
    ("start_10000730", "end_10000763"),
    ("start_10000731", "end_10000135"),
    ("start_10000736", "end_10000616"),
    ("start_10000735", "end_10000618"),

    #### Xe trống AF5
    ("start_10000191",),
    ("start_10000129",),
    ("start_10000603",),
    ("start_10000606",),
    ("start_10000608",),

    # #### Xe trống AF6
    ("start_10000764",),
    ("start_10000360",),
    ("start_10000625",),
    ("start_10000623",),
    ("start_10002180",),
    ("start_10002178",),
    #("start_10000278",),

    # Xe sach AF
    ("start_10001387", "end_10001979"),
    ("start_10001387", "end_10000725"),
    ("start_10001387", "end_10002015"),
    ("start_10001386", "end_10002016"),
    ("start_10001386", "end_10000728"),
    ("start_10001386", "end_10000733"),
    ("start_10001386", "end_10000737"),
    
    # 5U sub 5
    ("start_10001566", "end_10001827"), # 93-79
    ("start_10002148", "end_10001828"), # 93-79
    
    ("start_10002197", "end_10001818"), # 84-78
    ("start_10001568", "end_10001830"), # 84-78

    ("start_10002193", "end_10001832"), # 92-75
    ("start_10002191", "end_10001816"), # 92-76
    ("start_10001572", "end_10001829"), # 92-78
    ("start_10002188", "end_10001835"), # 92-78
    ("start_10001594", "end_10001833"), # 92-78
    ("start_10002189", "end_10001834"), # 92-78

    # Xe Sub 6 chuyen dung
    #("start_10002090", "end_10001492"), # 44-65
   
   
    ("start_10002018", "end_10001487"), # 49-1 # change end  from 1490 to 1487
    ("start_10002135", "end_10001346"), # 49-2 #
    ("start_10002141", "end_10001346"), # 49-3
    ("start_10001244", "end_10000772"), # 50
    ("start_10001245", "end_10002289"), # 50
    ("start_10001245", "end_10002291"), # 50
    ("start_10002145", "end_10000778"), # 51
    ("start_10001248", "end_10001490"), # 51 # change end from 1487 to 1490
    ("start_10001249", "end_10001486"), # 51

    # ### Xe trống sub 5
    # ("start_10000776", "end_10001546"),
    # ("start_10000782", "end_10001546"),
    # ("start_10001843", "end_10002171"),
    # ("start_10000888", "end_10001546"), 

    
]
PAIR_5L = [

      # Xe 5L-, 6L-
    ("start_10001980", "end_10002041"), #31-74 5L1-1
    ("start_10001981", "end_10001798"), #31-85 5L1-2
    ("start_10001851", "end_10002265"), #6L2-2
    # ("start_10001970", "end_10002175"), #34-70 5L2-1 doi sang 1976
    ("start_10001976", "end_10002175"), #32-70 5L2-1
    ("start_10000718", "end_10001693"), #34-81 5L2-2
    ("start_10000717", "end_10001694"), #34-81 5L2-3
    ("start_10001971", "end_10001695"), #34-82 5L2-4
    ("start_10001972", "end_10001696"), #34-82 5L2-5
    ("start_10001573", "end_10001828"), # 74-79


]
PAIR_6L = [
    ("start_10000739", "end_10001529"), #38-61 6L1-1
    ("start_10000740", "end_10001357"), #38-66 6L1-2

    ("start_10001852", "end_10002177"), #30-70 6L2-1
    ("start_10001850", "end_10001356"), #30-66 6L2-3
    ("start_10001849", "end_10001350"), #30-66 6L2-4
    ("start_10001848", "end_10001351"), #30-66 6L2-5
    ("start_10001847", "end_10001358"), #30-66 6L2-6
    # ("start_10001846", "end_10000787"), #43-60 6L2-7
    # ("start_10001845", "end_10000789"), #43-60 6L2-8
    ("start_10002395", "end_10002397"), #c46-3
    ("start_10001243", "end_10001485"), #c49-4
    ("start_10002084", "end_10001344"), #c45-3


]


# GUI theo vùng
VALIDATE_PAIRS_BY_ZONE = {
    "AE5": PAIRS_AE_5,
    "AE6": PAIRS_AE_6,
    "AF": PAIR_AF,
    "5L": PAIR_5L,
    "6L": PAIR_6L + PAIRS_SUB_5,
}
# VALIDATE_PAIRS = set(PAIR_AF + PAIR_5L + PAIR_6L + PAIRS_SUB_5)
VALIDATE_PAIRS = set(PAIRS_AE_5 + PAIRS_AE_6+ PAIR_AF + PAIR_5L + PAIR_6L + PAIRS_SUB_5)

# Simulate camera data (rtsp, rois, node_ids) - in real, import from camera_service.py
CAMERAS = [
     # -----------------AE5 CAMERA ------------------
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.102:554/Streaming/Channels/102", #AE
        "zone": "AE5",
        "rois": [
            {"node_id": "start_10000060", "roi": [163, 156, 79, 66]},
            {"node_id": "start_10000059", "roi": [491, 139, 73, 80]}
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.103:554/Streaming/Channels/102", #xe chuyên dụng chưa dùng
        "zone": "AE5",
        "rois": [
            {"node_id": "start_10001763", "roi": [183, 194, 33, 107]},
            {"node_id": "start_10001762", "roi": [247, 213, 45, 103]},
            {"node_id": "start_10002233", "roi": [293, 218, 42, 101]},
            {"node_id": "start_10002232", "roi": [ 357, 243, 69, 47]}
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.104:554/Streaming/Channels/102", #xe chuyên dụng chưa dùng
        "zone": "AE5",
        "rois": [
            {"node_id": "start_10002235", "roi": [268, 274, 80, 62]},
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.105:554/Streaming/Channels/102", # not recognize AE
        "zone": "AE5",
        "rois": [
            {"node_id": "start_10001057", "roi": [175, 93, 79, 62]},
            {"node_id": "start_10001056", "roi": [171, 162, 84, 74]},
            {"node_id": "start_10001055", "roi": [164, 233, 89, 75]},
            {"node_id": "start_10001054", "roi": [160, 312, 89, 69]},
            {"node_id": "end_10002015", "roi": [421, 154, 54, 45]}, #xe sach end
            {"node_id": "end_10002016", "roi": [423, 87, 55, 51]}, #xe sach end
        ]
    },
    { 
        "rtsp": "rtsp://admin:Thado12@@192.168.1.106:554/Streaming/Channels/102", #low conf + not recognize  AE
        "zone": "AE5",
        "rois": [
           # {"node_id": "start_10001059", "roi": [160, 156, 79, 71]},
            {"node_id": "start_10001050", "roi": [403, 77, 87, 65]},
            {"node_id": "start_10001051", "roi": [405, 158, 86, 71]},
            {"node_id": "start_10001052", "roi": [402, 245, 88, 72]},
            {"node_id": "start_10001053", "roi": [399, 326, 99, 72]}
        ]
    },

    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.110:554/Streaming/Channels/102", # trái sang phải AE
        "zone": "AE5",
        "rois": [
            {"node_id": "end_10000759", "roi": [89, 158, 108, 148]},
            {"node_id": "end_10000760", "roi": [217, 154, 136, 148]},
            {"node_id": "end_10000761", "roi": [356, 139, 111, 151]}
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.111:554/Streaming/Channels/102", #AE
        "zone": "AE5",
        "rois": [
            {"node_id": "end_10000396", "roi": [157, 154, 99, 105]},
            {"node_id": "end_10000394", "roi": [367, 195, 111, 55]}
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.112:554/Streaming/Channels/102",#AE
        "zone": "AE5",
        "rois": [
            {"node_id": "start_10000391", "roi": [25, 234, 107, 85]},
            {"node_id": "end_10000388", "roi": [145, 244, 108, 75]},
            {"node_id": "end_10000385", "roi": [258, 235, 121, 76]},
            {"node_id": "end_10000382", "roi": [376, 228, 124, 78]}
        ]
    },

    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.113:554/Streaming/Channels/102", 
        "zone": "AE5",
        "rois": [
            {"node_id": "start_10001287", "roi": [253, 185, 134, 142]}
            ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.115:554/Streaming/Channels/102",
        "zone": "AE5",
        "rois": [
            {"node_id": "start_10001290", "roi": [220, 212, 166, 109]}
            ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.114:554/Streaming/Channels/102", #qr code AE
        "zone": "AE5",
        "rois": [
            {"node_id": "end_10000379", "roi": [68, 205, 88, 149]},
            {"node_id": "end_10000376", "roi": [163, 199, 122, 164]},
            {"node_id": "end_10000373", "roi": [306, 200, 115, 160]},
            {"node_id": "end_10000370", "roi": [426, 209, 95, 143]}
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.116:554/Streaming/Channels/102", #qr_code AE
        "zone": "AE5",
        "rois": [
            {"node_id": "end_10000367", "roi": [197, 121, 65, 53]},
            {"node_id": "end_10000361", "roi": [282, 102, 75, 61]}, 
            {"node_id": "end_10001943", "roi": [391, 88, 90, 62]}, 
            {"node_id": "start_10001555", "roi": [ 241, 275, 134, 113]}
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.117:554/Streaming/Channels/102", #AE
        "zone": "AE5",
        "rois": [
            {"node_id": "start_10001299", "roi": [92, 356, 120, 90]},
            {"node_id": "start_10001295", "roi": [494, 291, 88, 43]}
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.118:554/Streaming/Channels/102", #AE
        "zone": "AE5",
        "rois": [
            {"node_id": "end_10001495", "roi": [420, 98, 124, 137]},
            {"node_id": "start_10001498", "roi": [92, 111, 87, 72]}  
        ]
    },


    # -----------------AE6 CAMERA ------------------
    #### ---- Xe cấp -----
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.107:554/Streaming/Channels/102",
        "zone": "AE6",
        "rois": [
            {"node_id": "start_10000037", "roi": [151, 258, 58, 111]},
            {"node_id": "start_10000038", "roi": [217, 268, 48, 113]},
            {"node_id": "start_10000039", "roi": [276, 278, 46, 110]},
            {"node_id": "start_10000040", "roi": [326, 282, 51, 115]},
            {"node_id": "start_10000041", "roi": [381, 290, 56, 113]},
            {"node_id": "start_10000042", "roi": [434, 298, 55, 108]}
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.119:554/Streaming/Channels/102",
        "zone": "AE6",
        "rois": [
            {"node_id": "end_10000266", "roi": [400, 218, 91, 39]},
            {"node_id": "end_10000757", "roi": [157, 208, 34, 85]},
            {"node_id": "end_10000758", "roi": [235, 270, 62, 120]},
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.120:554/Streaming/Channels/102",
        "zone": "AE6",
        "rois": [
            {"node_id": "end_10000267", "roi": [366, 274, 100, 86]},
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.121:554/Streaming/Channels/102", 
        "zone": "AE6",
        "rois": [
            {"node_id": "end_10000276", "roi": [231, 210, 90, 218]},
            {"node_id": "end_10000274", "roi": [165, 310, 48, 72]}, #6C4
            {"node_id": "start_10000278", "roi": [321, 257, 60, 125]}, #xt6
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.122:554/Streaming/Channels/102", 
        "zone": "AE6",
        "rois": [
            {"node_id": "end_10000268", "roi": [184, 153, 149, 109]}, #CD2
            #{"node_id": "end_10000268", "roi": [228, 122, 65, 177]}, #CD3
            {"node_id": "end_10000272", "roi": [391, 125, 63, 137]}, #CD3
        ]
    },
    # {
    #     "rtsp": "rtsp://admin:Thado12@@192.168.1.123:554/Streaming/Channels/102", 
    #     "zone": "AE6",
    #     "rois": [
    #         {"node_id": "start_10000910", "roi": [191, 258, 105, 91]}, #AE6-XT1
    #         {"node_id": "start_10000907", "roi": [321, 267, 89, 89]}, #AE6-XT2
    #     ]
    # },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.124:554/Streaming/Channels/102",
        "zone": "AE6",
        "rois": [
            {"node_id": "end_10000280", "roi": [221, 90, 106, 202]}, #-6C3
            {"node_id": "end_10000282", "roi": [326, 88, 96, 205]}, #-6C2
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.126:554/Streaming/Channels/102",
        "zone": "AE6",
        "rois": [
            {"node_id": "end_10000290", "roi": [190, 135, 94, 188]}, #CD6
            {"node_id": "end_10001797", "roi": [110, 145, 74, 172]}, #CD7
            {"node_id": "end_10000288", "roi": [289, 150, 96, 174]}, #-6C6
            {"node_id": "end_10000286", "roi": [389, 226, 51, 74]}, #-6C5
            
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.127:554/Streaming/Channels/102",
        "zone": "AE6",
        "rois": [
            {"node_id": "start_10000898", "roi": [224, 271, 122, 57]}, #AE6-XT-moi1
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.171:554/Streaming/Channels/102",
        "zone": "AE6",
        "rois": [
            {"node_id": "start_10000903", "roi": [147, 300, 123, 96]}, #AE6-XT3
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.141:554/Streaming/Channels/102",
        "zone": "AE6",
        "rois": [
            {"node_id": "start_10000989", "roi": [357, 244, 45, 97]} #6B-
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.142:554/Streaming/Channels/102",
        "zone": "AE6",
        "rois": [
            {"node_id": "start_10000992", "roi": [192, 110, 34, 89]}, #6A-
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.140:554/Streaming/Channels/102",
        "zone": "AE6",
        "rois": [
            {"node_id": "start_10000063", "roi": [266, 213, 88, 74]}, 
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.139:554/Streaming/Channels/102",
        "zone": "AE6",
        "rois": [
            {"node_id": "start_10000749", "roi": [ 490, 158, 52, 124]}, #CD2
            {"node_id": "start_10000748", "roi": [427, 149, 59, 135]}, #CD3
            {"node_id": "start_10000747", "roi": [359, 146, 58, 131]}, #CD4
            {"node_id": "start_10000746", "roi": [311, 190, 35, 104]}, #CD5
            {"node_id": "start_10002274", "roi": [247, 186, 31, 89]}, #CD6
            {"node_id": "start_10002273", "roi": [196, 195, 36, 80]}, #CD7
            {"node_id": "start_10002272", "roi": [110, 225, 71, 40]}, #CD8
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.128:554/Streaming/Channels/102",
        "zone": "AE6",
        "rois": [
            {"node_id": "end_10001793", "roi": [279, 247, 97, 60]}, #CD8
            {"node_id": "end_10001796", "roi": [436, 259, 107, 63]}, #CD7
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.129:554/Streaming/Channels/102",
        "zone": "AE6",
        "rois": [
            {"node_id": "start_10002278", "roi": [73, 271, 101, 59]}, #AE6-XT-moi2
            {"node_id": "start_10002276", "roi": [533, 228, 82, 52]}, #AE6-XT-moi3
        ]
    },

    # =============AF===============
    # Zone 5L
    # {
    # "rtsp": "rtsp://admin:Thado12@@192.168.1.173:554/Streaming/Channels/102", 
    # "zone": "5L",
    # "rois": [
    #     {"node_id": "end_10001994", "roi": [500, 130, 82, 90]}, # bỏ thay bằng cam 70

    #     ]
    # },
    {
    "rtsp": "rtsp://admin:Thado12@@192.168.1.181:554/Streaming/Channels/102", 
    "zone": "5L",
    "rois": [
        {"node_id": "end_10001693", "roi": [367, 124, 70, 126]},
        {"node_id": "end_10001694", "roi": [289, 128, 63, 137]},
        ]
    },
    {
    "rtsp": "rtsp://admin:Thado12@@192.168.1.182:554/Streaming/Channels/102", 
    "zone": "5L",
    "rois": [
        {"node_id": "end_10001695", "roi": [354, 86, 68, 117]},
        {"node_id": "end_10001696", "roi": [284, 88, 67, 127]},

        ]
    },
    {
    "rtsp": "rtsp://admin:Thado12@@192.168.1.185:554/Streaming/Channels/102", 
    "zone": "5L",
    "rois": [
        {"node_id": "end_10001798", "roi": [244, 122, 135, 248]},

        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.131:554/Streaming/Channels/102", 
        "zone": "5L",
        "rois": [
            {"node_id": "start_10001980", "roi": [325, 229, 37, 90]},
            {"node_id": "start_10001981", "roi": [281, 225, 37, 93]},
            {"node_id": "end_10001979", "roi": [433, 230, 36, 90]},
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.174:554/Streaming/Channels/102", 
        "zone": "5L",
        "rois": [
            {"node_id": "end_10002041", "roi": [161, 119, 52, 46]},
            {"node_id": "start_10002189", "roi": [44, 337, 33, 52]},
            ]
    },

    # ------------------6L------------------
    {
    "rtsp": "rtsp://admin:Thado12@@192.168.1.138:554/Streaming/Channels/102",
    "zone": "6L",
    "rois": [
        {"node_id": "start_10000739", "roi": [180, 145, 41, 83]},
        {"node_id": "start_10000740", "roi": [235, 144, 38, 87]},
        {"node_id": "end_10000737", "roi": [80, 159, 26, 88]},
        ]
    },
    {
    "rtsp": "rtsp://admin:Thado12@@192.168.1.161:554/Streaming/Channels/102",
    "zone": "6L",
    "rois": [
        {"node_id": "end_10001529", "roi": [294, 275, 70, 54]}, #6L1-1

        ]
    },
    #{
    #"rtsp": "rtsp://admin:Thado12@@192.168.1.152:554/Streaming/Channels/102",
    #"zone": "6L",
    #"rois": [
     #   {"node_id": "end_10001255", "roi": [319, 258, 46, 103]},
    #    {"node_id": "end_10001253", "roi": [196, 217, 48, 79]}, 6L2-1 cũ -> bỏ
      #  {"node_id": "end_10001254", "roi": [270, 306, 29, 65]},

       # ]
    #},
    {
    "rtsp": "rtsp://admin:Thado12@@192.168.1.166:554/Streaming/Channels/102",
    "zone": "6L",
    "rois": [
        {"node_id": "end_10001357", "roi": [305, 163, 86, 63]},
        {"node_id": "end_10001356", "roi": [199, 160, 80, 66]},
        {"node_id": "end_10001350", "roi": [136, 281, 67, 119]},
        {"node_id": "end_10001351", "roi": [244, 291, 64, 115]},
        {"node_id": "end_10001358", "roi": [320, 286, 62, 115]},
        ]
    },
    {
    "rtsp": "rtsp://admin:Thado12@@192.168.1.130:554/Streaming/Channels/102",
    "zone": "6L",
    "rois": [
       {"node_id": "start_10001852", "roi": [113, 352, 48, 106]}, #6L2-1
       {"node_id": "start_10001850", "roi": [235, 352, 47, 101]},
        {"node_id": "start_10001849", "roi": [290, 353, 52, 99]},
        {"node_id": "start_10001848", "roi": [349, 351, 46, 109]},
        {"node_id": "start_10001851", "roi": [166, 363, 39, 86]},
        # {"node_id": "start_10001847", "roi": [414, 360, 48, 102]}, # 6L2-6 moved to camera 43
        # {"node_id": "start_10001847", "roi": [409, 393, 54, 72]},

        ]
    },
    {
    "rtsp": "rtsp://admin:Thado12@@192.168.1.143:554/Streaming/Channels/102",
    "zone": "6L",
    "rois": [
        {"node_id": "start_10001847", "roi": [298, 400, 32, 50]}, # 6L2-6 moved from camera 30 to camera 43
        {"node_id": "start_10001846", "roi": [230, 373, 36, 74]}, # 6L2-7
        {"node_id": "start_10001845", "roi": [166, 366, 33, 80]}, # 6L2-8
        ]
    },
    {
    "rtsp": "rtsp://admin:Thado12@@192.168.1.170:554/Streaming/Channels/102", # 6L2-1  + 5L2-1  +  XT
    "zone": "6L",
    # "zone": "5L",
    "rois": [
        {"node_id": "end_10002177", "roi": [392, 328, 76, 57]},  #6L2-1
        {"node_id": "end_10002175", "roi": [252, 395, 80, 67]},    #5L2-1
        {"node_id": "start_10002180", "roi": [350, 183, 62, 71]}, #XT
        {"node_id": "start_10002178", "roi": [224, 227, 57, 87]}, #XT
        ]
    },
    {
    "rtsp": "rtsp://admin:Thado12@@192.168.1.188:554/Streaming/Channels/102",
    "zone": "6L",
    "rois": [
        {"node_id": "end_10002289", "roi": [179, 317, 85, 42]},
        {"node_id": "end_10002291", "roi": [289, 316, 85, 43]},
    ]
    },
    # {
    # "rtsp": "rtsp://admin:Thado12@@192.168.1.160:554/Streaming/Channels/102", // Duc comment ko dung
    # "zone": "6L",
    # "rois": [
    #     {"node_id": "end_10000787", "roi": [388, 160, 45, 78]},
    #     {"node_id": "end_10000789", "roi": [259, 153, 48, 85]},
       
    #     ]
    # },

        #-----------------AF Camera-----------------
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.132:554/Streaming/Channels/102", 
        "zone": "AF",
        "rois": [
            {"node_id": "start_10001976", "roi": [175, 253, 44, 110]}, #5L2-9 -> 5L2-1
            {"node_id": "start_10001975", "roi": [230, 251, 50, 115]},#5L2-8 -> 5L2-6
            {"node_id": "start_10001974", "roi": [295, 285, 42, 71]},#5L2-7
            # {"node_id": "start_10001973", "roi": [351, 283, 36, 75]},# Xe-Chan 5L2-6 doi sang 1975
            {"node_id": "start_10001972", "roi": [410, 292, 30, 66]},#5L2-5
            {"node_id": "start_10001971", "roi": [455, 275, 33, 83]},#5L2-4
           
        
            ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.133:554/Streaming/Channels/102", 
        "zone": "AF",
        "rois": [
            {"node_id": "start_10000707", "roi": [127, 210, 36, 110]},
            {"node_id": "start_10001978", "roi": [174, 213, 42, 107]},
            {"node_id": "start_10001977", "roi": [327, 227, 42, 113]},

            ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.134:554/Streaming/Channels/102",
        "zone": "AF",
        "rois": [
            {"node_id": "start_10000721", "roi": [346, 199, 46, 114]},
            {"node_id": "start_10000722", "roi": [414, 200, 46, 106]},
            {"node_id": "start_10000723", "roi": [461, 223, 44, 92]},
            # {"node_id": "start_10001970", "roi": [220, 207, 42, 106]}, #5L2-1 chuyen sang 1976
            {"node_id": "start_10000718", "roi": [163, 229, 36, 86]}, #5L2-2
             {"node_id": "start_10000717", "roi": [121, 229, 39, 89]},#5L2-3
            # {"node_id": "start_10001972", "roi": [49, 230, 29, 80]}, #5L2-5
        
            ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.136:554/Streaming/Channels/102", 
        "zone": "AF",
        "rois": [
            {"node_id": "start_10000728", "roi": [136, 223, 48, 104]},
            {"node_id": "start_10000730", "roi": [265, 232, 45, 88]},
            {"node_id": "start_10000731", "roi": [326, 236, 44, 93]}
            ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.137:554/Streaming/Channels/102", 
        "zone": "AF",
        "rois": [
            {"node_id": "start_10000733", "roi": [176, 133, 37, 104]}, ## Kiểm tra (xe trống)
            {"node_id": "start_10000735", "roi": [296, 142, 39, 92]},
            {"node_id": "start_10000736", "roi": [350, 141, 36, 93]}
            ]
    },
    { 
        "rtsp": "rtsp://admin:Thado12@@192.168.1.153:554/Streaming/Channels/102", 
        "zone": "AF",
        "rois": [
           {"node_id": "end_10000188", "roi": [183, 228, 70, 130]},
           {"node_id": "start_10000191", "roi": [ 103, 282, 60, 99]}
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.154:554/Streaming/Channels/102", 
        "zone": "AF",
        "rois": [
            {"node_id": "end_10000130", "roi": [238, 43, 75, 193]},
            {"node_id": "start_10000129", "roi": [341, 67, 71, 146]}
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.155:554/Streaming/Channels/102", 
        "zone": "AF",
        "rois": [
            {"node_id": "end_10000135", "roi": [129, 178, 70, 54]},
            {"node_id": "start_10000360", "roi": [ 128, 272, 75, 48]},
            {"node_id": "end_10000600", "roi": [424, 230, 82, 60]},
            {"node_id": "start_10000603", "roi": [425, 331, 80, 43]}
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.156:554/Streaming/Channels/102", 
        "zone": "AF",
        "rois": [
            {"node_id": "start_10000606", "roi": [202, 161, 42, 96]}, 
            {"node_id": "start_10000608", "roi": [263, 163, 38, 89]},
            {"node_id": "end_10000612", "roi": [306, 219, 73, 40]}, # 5M1
            {"node_id": "end_10000614", "roi": [390, 216, 64, 48]}, # 5M2
            {"node_id": "end_10002260", "roi": [82, 212, 62, 37]} # 5L2-6
            ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.157:554/Streaming/Channels/102", 
        "zone": "AF",
        "rois": [
            {"node_id": "start_10000625", "roi": [210, 213, 41, 103]},
            {"node_id": "start_10000623", "roi": [267, 212, 37, 100]},
            {"node_id": "end_10000616", "roi": [395, 255, 62, 47]}, # 6M2
            {"node_id": "end_10000618", "roi": [315, 257, 67, 48]}, # 6M1
            {"node_id": "end_10002265", "roi": [76, 258, 62, 49]} # 6L2-2
            ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.158:554/Streaming/Channels/102", 
        "zone": "AF",
        "rois": [
            {"node_id": "end_10000762", "roi": [198, 213, 45, 82]},
            {"node_id": "end_10000763", "roi": [257, 214, 42, 81]},
            {"node_id": "start_10000764", "roi": [313, 210, 47, 77]},
            ]
    },
    # {
    #     "rtsp": "rtsp://admin:Thado12@@192.168.1.194:554/Streaming/Channels/102", 
    #     "zone": "AF",
    #     "rois": [
    #         {"node_id": "start_10001387", "roi": [457, 126, 42, 103]}, #xe sach
    #         {"node_id": "start_10001386", "roi": [463, 267, 34, 96]}, #xe sach
    #         ]
    # },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.135:554/Streaming/Channels/102", 
        "zone": "AF",
        "rois": [
            {"node_id": "end_10000725", "roi": [257, 171, 52, 101]},
            {"node_id": "start_10000727", "roi": [390, 175, 38, 98]},
            ]
    },
    
    # # XE CHUYEN DUNG
     {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.193:554/Streaming/Channels/102", 
         "zone": "AF",
        "rois": [
             {"node_id": "start_10001566", "roi": [365, 264, 56, 48]},
             {"node_id": "start_10002148", "roi": [303, 276, 47, 49]},
             #{"node_id": "start_10002146", "roi": [225, 284, 47, 33]},
            ]
    },
    
     {
         "rtsp": "rtsp://admin:Thado12@@192.168.1.179:554/Streaming/Channels/102", 
         "zone": "AF",
         "rois": [
             {"node_id": "end_10001828", "roi": [138, 282, 76, 77]},
             {"node_id": "end_10001827", "roi": [282, 270, 95, 84]},
            ]
     },

     {
         "rtsp": "rtsp://admin:Thado12@@192.168.1.184:554/Streaming/Channels/102", 
        "zone": "AF",
        "rois": [
            {"node_id": "start_10002197", "roi": [317, 252, 48, 54]},
            #{"node_id": "start_10002193", "roi": [94, 245, 54, 61]},
            {"node_id": "start_10001568", "roi": [228, 255, 66, 60]},
             ]
     },

    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.178:554/Streaming/Channels/102", 
        "zone": "AF",
        "rois": [
            {"node_id": "end_10001829", "roi": [177, 150, 79, 62]},
            {"node_id": "end_10001830", "roi": [329, 275, 83, 73]}, 
            {"node_id": "end_10001816", "roi": [328, 153, 76, 58]},
            {"node_id": "end_10001818", "roi": [176, 277, 75, 66]},

            # {"node_id": "end_10001818", "roi": [164, 279, 79, 82]}, #1
            # {"node_id": "end_10001831", "roi": [176, 152, 68, 76]}, #2
            # {"node_id": "end_10001817", "roi": [289, 289, 68, 80]}, #4
            # {"node_id": "end_10001816", "roi": [408, 290, 86, 69]}, #5
            # {"node_id": "end_10001829", "roi": [412, 140, 74, 70]}, #6
            ]
    },

     {
         "rtsp": "rtsp://admin:Thado12@@192.168.1.192:554/Streaming/Channels/102", 
        "zone": "AF",
         "rois": [
             {"node_id": "start_10002193", "roi": [450, 259, 50, 69]},
             {"node_id": "start_10002191", "roi": [332, 274, 63, 62]},
             {"node_id": "start_10001572", "roi": [216, 274, 67, 62]},
             {"node_id": "start_10002188", "roi": [144, 282, 57, 59]},
             {"node_id": "start_10001594", "roi": [59, 284, 40, 56]},
             #{"node_id": "start_10002189", "roi": [19, 291, 38, 49]},
             ]
     },

     {
         "rtsp": "rtsp://admin:Thado12@@192.168.1.175:554/Streaming/Channels/102", 
         "zone": "AF",
         "rois": [
             {"node_id": "end_10001834", "roi": [122, 256, 60, 98]},
             {"node_id": "end_10001833", "roi": [243, 252, 86, 107]},
             {"node_id": "end_10001832", "roi": [383, 256, 75, 91]},
            ]
     },

    # {
    #     "rtsp": "rtsp://admin:Thado12@@192.168.1.186:554/Streaming/Channels/102", // Duc comment ko dung
    #     "zone": "AF",
    #     "rois": [
    #         {"node_id": "start_10002227", "roi": [80, 159, 26, 88]},
    #         ]
    # },


     {
         "rtsp": "rtsp://admin:Thado12@@192.168.1.176:554/Streaming/Channels/102", 
         "zone": "AF",
         "rois": [
            # {"node_id": "end_10001834", "roi": [424, 42, 35, 88]}, # no cam
             {"node_id": "end_10001835", "roi": [342, 63, 43, 50]}, 
             ]
     },
    # {
    #     "rtsp": "rtsp://admin:Thado12@@192.168.1.197:554/Streaming/Channels/102", // Duc comment ko dung
    #     "zone": "AF",
    #     "rois": [
    #         {"node_id": "end_10000890", "roi": [385, 281, 33, 44]},
    #         {"node_id": "start_10000888", "roi": [266, 274, 29, 58]} # XT
    #         ]
    # },
    # ### Sub 6
    #  ### -------------------- Sub 6 -------------------------------
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.144:554/Streaming/Channels/102",
        "zone": "Sub6",
        "rois": [
            {"node_id": "start_10002090", "roi": [291, 332, 98, 80]},
            {"node_id": "start_10002091", "roi": [205, 331, 83, 86]},
            {"node_id": "start_10002088", "roi": [ 95, 347, 34, 54]}, #
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.145:554/Streaming/Channels/102",
        "zone": "Sub6",
        "rois": [
            {"node_id": "start_10002086", "roi": [176, 195, 81, 81]},
            {"node_id": "start_10002084", "roi": [273, 196, 78, 65]}, 
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.146:554/Streaming/Channels/102",
        "zone": "Sub6",
        "rois": [
            {"node_id": "start_10002082", "roi": [210, 298, 83, 101]}, #c46-1
            {"node_id": "start_10002393", "roi": [326, 316, 77, 88]}, #c46-2
            {"node_id": "start_10002395", "roi": [135, 319, 71, 78]}, # c46-3

        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.159:554/Streaming/Channels/102",
        "zone": "Sub6",
        "rois": [
            {"node_id": "start_10000776", "roi": [195, 174, 46, 96]},
            {"node_id": "start_10000782", "roi": [191, 284, 51, 104]},
            {"node_id": "end_10000772", "roi": [374, 161, 49, 78]},
            {"node_id": "end_10000778", "roi": [384, 262, 50, 98]}
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.180:554/Streaming/Channels/102",
        "zone": "Sub6",
        "rois": [
            {"node_id": "start_10001843", "roi": [406, 253, 149, 97]},
            {"node_id": "start_10001842", "roi": [222, 275, 171, 84]}, 
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.165:554/Streaming/Channels/102",
        "zone": "Sub6",
        "rois": [
            {"node_id": "end_10001492", "roi": [192, 160, 85, 130]}, # no cam # normal path not rack in map editor
            {"node_id": "end_10001493", "roi": [122, 219, 42, 46]}, # no cam # normal path not rack in map editor
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.164:554/Streaming/Channels/102",
        "zone": "Sub6",
        "rois": [
            {"node_id": "end_10001490", "roi": [222, 109, 111, 73]},
            {"node_id": "end_10001489", "roi": [351, 102, 95, 56]},
            {"node_id": "end_10001487", "roi": [350, 238, 104, 99]}, 
            {"node_id": "end_10001488", "roi": [229, 245, 88, 84]},
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.162:554/Streaming/Channels/102",
        "zone": "Sub6",
        "rois": [
            {"node_id": "end_10001486", "roi": [190, 206, 92, 137]},
            {"node_id": "end_10001485", "roi": [360, 227, 101, 128]},
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.168:554/Streaming/Channels/102",
        "zone": "Sub6",
        "rois": [
            {"node_id": "end_10001341", "roi": [340, 118, 57, 93]} 
            
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.169:554/Streaming/Channels/102",
        "zone": "Sub6",
        "rois": [
            {"node_id": "end_10001343", "roi": [223, 203, 89, 95]},
            {"node_id": "end_10001344", "roi": [450, 249, 68, 79]},
        ]
    },
    # {
    #     "rtsp": "rtsp://admin:Thado12@@192.168.1.172:554/Streaming/Channels/102", // Duc comment ko dung
    #     "zone": "Sub6",
    #     "rois": [
    #         {"node_id": "end_10002171", "roi": [250, 151, 114, 105]},
    #         {"node_id": "start_10002172", "roi": [391, 161, 97, 92]},
    #         {"node_id": "start_10002173", "roi": [511, 173, 63, 69]} 
    #     ]
    # },

    # ####SUB6
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.149:554/Streaming/Channels/102",
        "zone": "Sub6",
        "rois": [
            {"node_id": "start_10002018", "roi": [45, 174, 43, 76]},
            {"node_id": "start_10002135", "roi": [123, 259, 48, 104]}, 
            {"node_id": "start_10002141", "roi": [254, 265, 44, 64]}, 
            {"node_id": "start_10001243", "roi": [327, 260, 35, 65]}, 
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.150:554/Streaming/Channels/102",
        "zone": "Sub6",
        "rois": [
            {"node_id": "start_10001244", "roi": [178, 162, 42, 75]}, 
            {"node_id": "start_10001245", "roi": [253, 143, 46, 90]},
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.151:554/Streaming/Channels/101",
        "zone": "Sub6",
        "rois": [
            {"node_id": "start_10002145", "roi": [137, 230, 56, 65]},
            {"node_id": "start_10001248", "roi": [247, 221, 68, 72]},
            {"node_id": "start_10001249", "roi": [340, 212, 64, 71]}, 
        ]
    },
    {
        "rtsp": "rtsp://admin:Thado12@@192.168.1.167:554/Streaming/Channels/102",
        "zone": "Sub6",
        "rois": [
            {"node_id": "end_10001346", "roi": [358, 162, 50, 149]}, #c49-3
        ]
    },      
]

RTSP_AE5 = set(c["rtsp"] for c in CAMERAS if c.get("zone") == "AE5")
RTSP_AE6 = set(c["rtsp"] for c in CAMERAS if c.get("zone") == "AE6")
RTSP_5L = set(c["rtsp"] for c in CAMERAS if c.get("zone") == "5L")
RTSP_6L = set(c["rtsp"] for c in CAMERAS if c.get("zone") == "6L")
RTSP_AF = set(c["rtsp"] for c in CAMERAS if c.get("zone") == "AF")