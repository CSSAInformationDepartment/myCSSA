
#              ,' ``',
#             '  (o)(o)
#            `       > ;
#            ',     . ...-'"""""`'.
#          .'`',`''''`________:   ":___________________________________
#        (`'. '.;  |           ;/\;\;                                  |
#       (`',.',.;  |                                                   |
#      (,'` .`.,'  |    Mail Owl -> RESTful email service interface    |
#      (,.',.','   |              ~ Universal Component of openALICE   |
#     (,.',.-`_____|                                                   |
#         __\_ _\_ |              Designer: Le Lu (2019)               |
#                  |               Ver: 0.0.2 (Ricecake)               |
#                  |                 M.I.T. Licensed                   |
#                  |___________________________________________________|
#


# This is the communication module of Mail Owl
# It will listen to port 44300 in the gateway

# 组网思路
# 1. 获取服务器容器的IP地址
# 2. 向同网关下的44300端口广播自己的IP地址
# 3. 收听其他节点44300端口发出的IP的地址，并记录
# 4. 在添加任务时，根据收到节点广播的数量，进行负载分配（Round Robin）
