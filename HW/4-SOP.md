直接看 VBS业务流程梳理.docx

SOP可能需要的平台
# 01 操作检测
- 告警等基本检测（必选，勿删）：
	- **CMA告警平台**，查看对应region无未恢复的紧急告警
    ![](./images/1721698683445_image.png)
- 拨测检测（必选）
	- **拨测平台CloudMonitorSonar**。查看对应的region 1分钟拨测任务（任务名称中包含1minDiskTest 的拨测任务）最新一次任务执行成功
    ![](./images/1721698689892_image.png)
- 观察客户连接数和带宽
	- **TSC平台**，根据账号名和EFS实例id，查看待操作实例的客户连接数和带宽情况。
    ![](./images/1721699084419_image.png)
- 查询client节点配置
	- 登录任一**client节点**，执行cat /opt/sfs/client/config/client.cfg，查看当前client节点配置
    - 登录任一**client节点**，执行以下命令查询client版本和agent版本，并做好记录
1、cat /opt/sfs/client_version_record
2、cat /opt/sfs/agent_version_record
- 获取待修改client节点instid
	- 登录**CAC平台**，搜索efs_cluster_key_info_query，执行
参数1：--clusterid=$.{clusterid}
执行用户：root
超时时间：300s
目标主机选择对应局点任一EFS-Services节点点击执行
记录所有client节点instid
- 获取待迁移EFS卷对应的EFS实例
	- 登入**云服务开发平台**，点击操作平台，选择Region视图，选择对应的局点，EFS-》EFS-Services-》EFS-MySQL-network
	- 输入SELECT instId FROM rds_resource WHERE id IN ('$.{volume_id1}', '$.{volume_id2}')，点击执行，获取EFS实例clusterid
	- 记录以上获取的clusterid，用于后续操作
    ![](./images/1721699388595_image.png)

- 单、双层、混改架构判断
    1、登录**ServiceCM**，系统-》本地系统-》Region-》Service CM部署类型
    2、登录**ServiceCM**，云硬盘-》查看pod信息
（1）双层架构：Service CM部署类型显示为级联/被级联，有cascading-region和cascaded pod信息
![](./images/1721699595051_image.png)
（2）单层架构：Service CM部署类型显示为单层，有cascading-region，无cascaded pod信息
![](./images/1721699611289_image.png)
（3）混改架构：Service CM部署类型显示为单层，有cascading-region、cell pod和cascaded pod信息
![](./images/1721699623955_image.png)
- 存储池信息
1、**FSM portal**-》资源-》存储池
2、获取待解关联存储池名称及对应存储池ID
![](./images/1721699715246_image.png)
