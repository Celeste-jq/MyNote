# FSM
![](./images/1721614043226_image.png)
![](./images/1721614480539_image.png)
![](./images/1721614536435_image.png)
![](./images/1721614828255_image.png)


# FusionStorage
主要看链接
http://3ms.huawei.com/km/blogs/details/5308877
http://3ms.huawei.com/km/blogs/details/8654815

![](./images/1721631904613_image.png)

## ZK Zookeeper
- 分布式服务框架，负责统一命名服务、状态同步服务、集群管理、分布式应用配置项的管理
- MDC需要zk来保存元数据
- MDC主备管理：MDC模块进程启动后，各个MDC进程会向ZK注册选主，先注册的为主MDC；运行过程中，ZK记录MDC主备信息，并通过心跳机制监控MDC主备健康状况，一旦主MDC进程故障，会触发MDC重新选主。
- 数据存储：在MDC运行过程中，会生成各种控制试图信息，包括目标视图、中间视图、IO视图，这些信息的保存、更新、查询、删除操作都通过ZK提供的接口实现
- 数据同步：数据更新到主ZK，主ZK自动同步到两个备ZK，保证主备实时同步。

## MDC Metadata Controller
- 通过Partition分配算法，实现数据多分副本的RAID可靠性
- 通过与OSD、VBS间的消息交互，实现对OSD、VBS节点的状态变化的获取与通知
- 通过与Agent间的消息交互，实现系统的扩减容、状态查询、维护等
- 通过心跳检测机制，实现对OSD、VBS的状态监控

## VBS
- 作为FusionStorage系统存储功能的介入侧，负责卷和快照的管理功能、IO的介入和处理
- VBS和MDC的交互主要在于视图的获取，用于数据路由的计算，但由于VBS有视图缓存，该交互仅在VBS视图与MDC视图不一致情况下发生
- VBS通过Client模块与OSD资源池进行交互

## OSD
- FusionStorage存储池管理的每个物理磁盘对应一个OSD进程，OSD进程负责磁盘的管理、IO的复制、IO数据的Cache处理
- OSD通过强一直复制协议保证主备OSD的一致性




---
---


# 看视频笔记
![](./images/1721614721141_image.png)
![](./images/1721616945084_image.png)
FSM是负责运维的入口，涉及存储池创建、进程管理、进程监控、服务器管理、集群告警...
MDC负责管理数据路由，映射关系、路由表，管理池中OSD的online与offline等
VBS客户端，读写请求映射到存储池的磁盘上，请求转发
存储池与存储池之间物理隔离，每个存储池介质可能不一样（紫色）

![](./images/1721617151178_image.png)
DHT一致性哈希，用于解决数据寻址问题，将用户在卷上的数据放在某个存储池的某个硬盘上。

![](./images/1721617277872_image.png)
资源池即存储池，逻辑LBA地址通过DHT环映射，最终将用户数据打散到存储池的硬盘上，实现负载均衡。

![](./images/1721617301009_image.png)
考虑到磁盘可能会出现故障或重启，为了数据可靠性，实现副本机制，一份数据放在多个服务器上，多个服务器是分布在多个机柜上，实现机柜级的备份。

![](./images/1721617660465_image.png)
云盘挂给虚拟机后，用户看到卷，得到LBA地址，对LBA地址进行写数据，经过协议转换，经过VBS客户端，通过访问卷和LBA地址获得一个Key值，作为哈希索引，进行一致性哈希，得到一个Pt值，根据这个Pt值判断数据将落在哪个资源池哪个磁盘上，然后将读写请求转发到对应磁盘的OSD进程上，OSD收到请求后，磁盘与OSD也有一个映射表，记录OSD到磁盘的某个位置。

![](./images/1721617679822_image.png)
VBS主要作为存储池的接入端。
管理面：负责卷与快照的管理功能，通过VBM模块进行管理，所有请求都会转发到VBM模块。
数据面：数据路由，数据从OS内核到用户态 到SCSI模块，SCSI模块即一致性哈希部分，再到CLIENT模块，即请求路由OSD

![](./images/1721617961339_image.png)
OSD收到IO请求后，
RSM负责一致性协议，写一个数据，写多个副本，保证副本之间的一致性
SNAP完成Key到磁盘那个步骤
CACHE进行缓存，缓存管理、写入读取、flush
AIO盘卡读写

![](./images/1721618117014_image.png)
OSD磁盘管理方法：将磁盘空间按照1M粒度进行均匀切割，进行空间分配与释放。
如果需要1K，仍会按照1M去分配。
Metadata存放KeyValue映射关系，请求到磁盘的路由操作

![](./images/1721618216009_image.png)
MDC 保证系统可靠性，存放数据路由的元数据信息。
![](./images/1721618402547_image.png)
MDC管理OSD，保证OSD一致性

![](./images/1721618470745_image.png)
![](./images/1721618670301_image.png)
![](./images/1721618825847_image.png)
![](./images/1721618915855_image.png)
![](./images/1721619032564_image.png)
![](./images/1721619178600_image.png)
![](./images/1721619299508_image.png)
