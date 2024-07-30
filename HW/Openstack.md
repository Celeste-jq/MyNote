官网文档 https://docs.openstack.org/mitaka/zh_CN/install-guide-rdo/overview.html

【OpenStack原理及在华为云中的应用-哔哩哔哩】 https://b23.tv/IOADDsN


# 云计算与虚拟化
- 虚拟化：聚焦利用资源。在一个物理机上虚拟化出多个虚拟机，提高资源利用率。实现虚拟化后可以实现应用于物理资源的隔离，环境隔离，降低隔离损耗。
- 云计算：聚焦服务。将IT系统能力以服务的形式提供给用户使用，按需使用，按使用量收费。多租户隔离、负载隔离、资源隔离。

关系：
- 如果系统是经过虚拟化的，就可以以虚机作为服务发放给用户。

# 云与操作系统
Openstack是云服务器操作系统。
从操作系统的功能上：
- 资源抽象：把资源抽象成软件可以使用的资源形态。例如：各种品牌的手机会把硬件抽象成接口供软使用，因此软件可以在各种品牌手机上使用。
- 资源分配与负载调度：资源如何在软件之间进行分配。云计算平台上也会有很多种应用，需要资源分配与资源调度。
- 应用生命周期管理：例如手机软件的安装、使用、卸载。在云计算平台上应用的部署、运行、扩容、缩容、删除，也可以由openstack进行管理。
- 系统运维：系统监控、运维。
- 人机交互：提供界面给管理员或给最终用户。


# Openstack定义
- OpenStack是一个云操作系统，通过数据中心可控制大型的计算、存储、网络等资源池。
- 所有的管理通过前端界面管理员就可以完成，同样也可以通过web接口让最终用户部署资源。
- OpenStack的各个服务可以分布式部署，服务中的组件也可以分布式部署。
- OpenStack通过各种补充服务提供基础设施即服务 Infrastructure-as-a-Service (IaaS) 的解决方案。每个服务都提供便于集成的应用程序接口Application Programming Interface (API)。

# OpenStack服务
## KeyStone
为其他OpenStack服务提供认证和授权服务，为所有的OpenStack服务提供一个端点目录。
- 功能
	- 管理用户及其权限。 用户（User）指代真正的用户、其他系统和服务。
    - 维护OpenStack Services的Endpoint
    - Authentication（认证）：User访问OpenStack时向Keystone提交用户名的密码形式的Credentials，KeyStone验证后会给User签发一个Token作为后续访问的Credential
    - Authorization（鉴权）
- 相关概念
	- Endpoint：是一个网络上可访问的地址，通常是一个URL。Service通过Endpoint暴露自己的API。Keystone负责管理和维护每个Service的Endpoint。
    - Project：根据Openstack服务的对象不同，Project可以是一个客户（公有云，也叫租户）、部门或者项目组（私有云）
	    - 用于将Openstack的资源（计算、存储和网络）进行分组和隔离
        - 资源的所有权属于Project，而不是User
        - Project = Tenant = Account

## Glance
存储和检索虚拟机磁盘镜像，OpenStack计算会在实例部署时使用此服务。提供Image Service，管理Image，让用户能够发现、获取和保存Image
- 功能
	- 提供REST API 让用户能够查询和获取image的元数据和image本身
    - 支持多种方式存储image，包括普通的文件系统、Swift、Amazon Z3等
    - 对Instance执行Snapshot创建新的image

## Nova
在OpenStack环境中计算实例的生命周期管理。按需响应包括生成、调度、回收虚拟机等操作。
Nova 支持创建虚拟机、裸机服务器（通过使用 ironic），并且对系统容器提供有限的支持。Nova 作为一组守护进程在现有 Linux 服务器上运行以提供该服务。
- Nova-scheduler：虚机调度服务，负责决定在哪个计算节点上运行虚机
	- 用户创建Instance时，用户会提出资源需求，例如CPU、内存、磁盘。Openstack将这些需求定义在flavor中，用户只需要指定用哪个flavor就可以
    - 调度的实现方式-配置三个参数
	    - 默认Filter Scheduler调度器
        - scheduler_available-用于配置scheduler可用的filter，默认是所有nova自带的filter都可以用于过滤
        - scheduler_default_filters-用于指定scheduler真正使用的filter
- Nova-compute：通过Driver架构支持多种Hypervisor
	- 定期向Openstack报告计算节点的状态
    - 实现instance生命周期的管理

## Cinder
- 为云平台提供统一接口，按需分配的，持久化的块存储服务。
- 核心功能是对卷的管理，允许对卷、卷的类型、卷的快照、卷备份进行操作。
- 为后端不同的存储设备提供了统一的接口，不同的块设备服务厂商在Cinder中实现其驱动支持以与Openstack进行整合。
- 为运行实例而提供的持久性块存储。它的可插拔驱动架构的功能有助于创建和管理块存储设备。

组件：
- cinder-api提供北向接口，对客户请求进行校验工作，接口使用Restful风格
- cinder-scheduler负责调度工作，任务调度会涉及各类的过滤器以及权重器
- cinder-volume负责实际执行，对接块存储服务。

在Openstack中提供块存储服务
- volume provider - 数据的存储设备，为volume提供物理存储空间。cinder-volume支持多种volume provider，每种provider通过自己的driver与cinder-volume协调工作
- Create Volume
	- cinder-api - 收到 POST 后启动 volume_create_api flow（工作流）
	    - Success 状态代表api已经成功处理了创建请求并将消息发送给inderscheduler，并非完成了在存储节点上的创卷
        - volume_create_api 工作流包含若干Task，执行状态会经历PENDING, RUNNING和SUCCESS三个阶段
            a) ExtractVolumeRequestTask - 获取request信息
            b) QuotaReserveTask - 预留配额
            c) EntryCreateTask - 在数据库中创建volume条目
            d) QuotaCommitTask - 确认配额
            e) VolumeCastTask - 向cinder-scheduler发送消息（MQ），开始调度工作

	- cinder-scheduler - 执行调度 - volume_create_schedulerflow
	    - ExtractSchedulerSpecTask
        - ScheduleCreateVolumeTask - 完成 filter 和 weighting
        a) AvailabilityZoneFilter
        b) CapacityFilter
        c) CapabilitiesFilter
        d) CapacityWeigher
	    - 完成后发消息（经由MQ）给 cinder-volume，让其完成 volume 的创建
    - cinder-volume - 通过 driver 创建 volume - volume_create_managerflow
	    - 创卷前的准备任务
        a) ExtractVolumeRefTask
        b) OnFailureResheduleTask
        c) ExtractVolumeSpecTask
        d) NotifyVolumeActionTask
		- 创卷 CreateVolumeFromSpecTask
        - 收尾工作 CreateVolumeOnFinishTask

## Neutron
- 为整个Openstack环境提供网络支持，包括二层交换、三层路由、负载均衡、防火墙和VPN等
- 管理的网络资源
	- Network：隔离的二层广播域，支持多种类型
    - Subnet：instance的ip从subnet中分配
    - Port：prot可以看做虚拟交换机上的一个端口。port上定义了MAC地址和IP地址，当instance的虚拟网卡VIF绑定到port时，port会将MAC和IP分配给VIF
- Project, Network, Subnet, Port, VIF 之间的关系： 
	- Project 1 : m Network 1 : m Subnet 1 : m Port 1 : 1 VIF m : 1 Instance
