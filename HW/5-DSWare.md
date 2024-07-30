http://plm-pia.huawei.com/detaildocs?oid=VR:wt.doc.WTDocument:19828738134

![](./images/1721717661835_image.png)
# 块虚拟化
与传统存储以磁盘为管理单位不同，DSWare以块虚拟化为管理单位，即把传统数据按块按物理磁盘集中存储改成资源池统一管理条带化为单位打散存储，即DSWare下把集群里的所有物理机磁盘全部组成一个（或若干）大虚拟存储池，以一定块大小（1MB为单位）划分为条带，然后以一定算法保证数据相对均匀地hash到各个物理磁盘（hash分布）

# DSWare系统术语
在了解DSWare系统之前先了解一下DSWare中的关键术语（这里暂时看不懂没关系）
![](./images/1721718355344_image.png)
从上图上，DSWare的存储组织，其中p实体代表partition。
（1）	DHT:Distributed Hash Table，目前在DSWare中主要进行数据分区路由，是一种数据路由算法。
（2）	Partition：数据分区，DHT环上分割的基本单元，同时也是路由条目单元，在存储底层代表了一大块数据区域，内部会有多个key-value块。
（3）	Key-value：底层硬盘上的数据组织成key-value的形式，每个Key-value代表一个打散的数据块，数据块的大小一般为1M。
（4）	资源池：资源池是一个虚拟化的池，很多事数据卷可以共享一个资源池内，同一个卷的数据可以在资源池内打散到所有磁盘上；
（5）	故障域：相互之间不存在副本或RAID关系的磁盘组，本域内坏盘不影响其它域；一个资源池可以包含多个故障域，一个故障域也可以属于多个资源池，一块磁盘只能属于一个故障域，但可以属于多个资源池。
（6）	Volume：应用卷，代表了应用看到的一个LBA连续线性空间（LBA是操作系统的一种磁盘编址方式，详细查百度），一个volume只能属于一个资源池。

# DSWare业务进程部署图
图里不包括 agent管理维护进程， 也不包括开源的主备仲裁进程zookeeper进程。
![](./images/1721718750802_image.png)
DSWare在业务方面有MDC，VBS，OSD三类进程，每个CNA节点上VBS和MDC都是单进程的，OSD是多进程的，一个物理硬盘就由一个OSD进程管理。
**业务相关：**
1. DSWare VBS：主要完成了无状态的机头逻辑，对应用实现了基于SCSI块设备的访问接口(iscsi 模块)，同时完成块存储元数据的保存和访问逻辑。其中VBS的client主要接受MDC下发的IO view视图，然后根据视图规则，将数据转发到对应的OSD节点上，Client模块是一个无状态接口层，所以client和client之间不存在关系，它只从MDC上获取IO View视图或者是MDC主动通知它，或者主动从MDC进行查询，然后换成这些IO View，以减少与MDC的通信压力。

2. DSWare OSD：OSD是一个功能逻辑比较复杂的子系统，主要是根据MDC下发的partition View建立与备OSD的复制关系，然后接受VBS client发来的读写命令，完成数据的存放与获取，另外在节点故障或者恢复的时候，需要进行数据的同步，这些都是强一致性复制协议控制完成的。OSD主要包含了如下模块：
1）	RSM：分布式控制状态机，实现强一制性复制协议。
2）	Snapshot/Linked Clone：实现快照和链接克隆的模块
3）	Cache：读写cache功能，同时实现对机械磁盘的优化调度。
4）	VBD：将磁盘数据组织成DSWare系统的key-value访问方式
5）	Disk Manager：对磁盘IO进行错误处理，磁盘预测等。

3. DSWare MDC：MDC实现了分布式集群的状态视图控制，以及多节点加入、退出集群进行的IO视图、分区分配视图、节点视图的变更；同时控制了数据分布规则、数据重建规则。归纳以下功能：
（1）	重要数据的可靠保存，如OSD View，Partition View等重要数据
（2）	OSD状态变化获取通知
（3）	Partition的分配算法
（4）	心跳检测功能。

**管理部署相关：**
4. DSWare Agent：完成安装部署，完成进程监控等功能。
5. DSWare manage：集成到GM 完成安装部署、扩容减容，补丁升级等管理


# DSWare进程工作粗略介绍
DSWare进程介绍完毕后，粗略这些进程怎么配合？该干些什么？
1. 配置仲裁进程zookeeper并启动（著名开源代码，详细功能可查百度，这里只需要知道它唯一作用是通过它选MDC即可。）
2. 启动MDC进程，并发送消息到zookeeper确定自己是否做leader。如果被选做leader则等待OSD进程的上报。
3. 启动OSD进程，OSD进程启动首先完成自身硬盘等健康的检测，正常后初始化成功根据配置与所有MDC地址发送TCP/IP连接查询MDC leader，确定MDC leader，OSD与MDC leader建立长连接定时发送心跳并上报状态。（对MDC leader来说收到上报变更后，调整生成的 OSD view， partition view及IO view， 并把更新后的view主动更新到VBS和OSD，同时对其他非leader的MDC节点进行数据同步，这个非常类似CDN中MC接收MX/MS的路由上报后的生成路由数据的处理过程）。
4. 启动VBS进程。
（1）	VBS进程启动时首先主动连接MDC，获取MDC中的视图（主要由VBS的client模块获取IO view并保存），当获取视图成功后就意味着机头VBS对OSD分布数据，数据怎么访问就清楚了。
（2）	VBS获取视图完毕后发送自己的信息（IP/PORT）到MDC确定自己是否做leader，如果是确认自己选为leader，则向OSD读取元数据（元数据里保持着卷、快照信息及卷、快照挂载对应主机等核心信息）。如果自己不是leader则到leader的VBS的处同步元数据到本地。并把元数据并按hash方式在内存建key-value立映射关系（主要加快访问速度）。

完全启动流程图：
![](./images/1721720132488_image.png)


# DSWare数据分布
DSWare视图
![](./images/1721720874821_image.png)
DSWare系统中包含OSD View，IO View和Partition View 三种视图，它们的关系如图。存在的关系如下：
（1）	OSD View: 只存在MDC
（2）	Partition View：存在与MDC和主OSD
（3）	IO View：存在与MDC和主OSD备OSD及VBS Client。
在这不禁会问，OSD不是一个磁盘对应一个OSD，各自独立的吗？为啥出现主备？其实这里OSD主备是相当Partition View来说，是实现备份强一直行复制的需要，下面大致说一下主备OSD由来：
假设DSWare系统里总共有3台机器，每个机器上有2个硬盘，MDC的partition算法分为24个partition（partition算法比较复杂，这里不讨论），初始化放置时，每个OSD将会承载4个主partition的数据，4个备partion的数据。如图：（图中partition简写为p）
![](./images/1721720983910_image.png)
对于OSD1上P1来说，它的备份数据P1’，即在OSD2节点上。所以对于partition1来说主OSD为OSD1和备OSD为OSD2.这样OSD1和OSD2组成了一对复制关系。而对于P5来说，OSD2是它的主节点，OSD1是它的备节点，所以谈到OSD主和备，都是针对partition来说的，并不是我们进程上所说的主备。




