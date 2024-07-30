![](./images/1722245427548_image.png)
1.每个Controller都会继承BaseController
BaseController中有各种响应体ResponseBean、对响应码的设置、日志操作以及鉴权方法
2.进行业务前都会进行鉴权

```java
checkTokenValid(Constants.FRIDAY_READER_ROLES, false);
```
此时会使用BseController的鉴权方法

```java
    /**
     * 判断用户是否具有执行权限
     * 1.token的有效性判定，包括解析、格式，是否过期
     * 2.获取当前用户token中优先级最高的角色
     * 3.判断用户最高优先级的role是否存在于当前接口的可操作角色列表，如果存在，则允许接口调用，否则拦截报错
     * @param actionRoles 有接口调用权限的操作角色列表
     * @param needSysAdmin 有的接口属于friday系统的专属接口，只有Friday的EvsFriday_sysadmin权限的才能调用，true即必须是sysadmin的role，false即不必
     * @throws OperationException 异常
     */
    protected JwtToken checkTokenValid(String actionRoles, boolean needSysAdmin) throws OperationException {
        // 开关关闭 并且 不是reader权限的接口, 拦截
        if (!allowOperateAction && !Constants.FRIDAY_READER_ROLES.equals(actionRoles)) {
            throw new OperationException(ErrorConstants.INTERNAL_ERROR, "Operation is Forbidden in this system.");
        }

        JwtToken tokenObject = BaseOperatorContextUtils.getToken();

        if (tokenObject == null || tokenObject.getUserInfo() == null || tokenObject.getExpiredAt() == null) {
            LOGGER.error("parse token, the object invalid, object: {}", JsonUtil.toJson(tokenObject));
            throw new OperationException(ErrorConstants.COP_PARSE_TOKEN_OBJECT_INVALID);
        }

        if (Long.parseLong(tokenObject.getExpiredAt()) < System.currentTimeMillis()) {
            LOGGER.error("token expired.");
            throw new OperationException(ErrorConstants.COP_TOKEN_EXPIRED);
        }

        if (needSysAdmin) {
            if (hasAdminRole(tokenObject)) {
                return tokenObject;
            } else {
                LOGGER.error("the operator has no admin role, forbidden operating.");
                throw new OperationException(ErrorConstants.COP_TOKEN_SHOULD_HAS_SYS_ADMIN_ROLE);
            }
        }

        //获取用户的当前权限（即最大优先权角色）
        String userPriorityRole = getPriorityRole(tokenObject);
        LOGGER.info("This operator has the priority role: {}", userPriorityRole);

        if (userPriorityRole == null || !isAllowedAction(userPriorityRole, actionRoles)) {
            LOGGER.error("token role has no rights to operate this api.");
            throw new OperationException(ErrorConstants.COP_TOKEN_HAS_NO_ACCESS);
        }

        return tokenObject;
}
```
从BaseOperatorContextUtils类中获取Token
```java
public class BaseOperatorContextUtils {

    private BaseOperatorContextUtils() {
    }

    public static final String TOKEN_OBJECT = "token_object";

    public static final String REGION_ID = "region_id";

    private final static Map<String, ThreadLocal<?>> MAP = new HashMap<>();

    private static final ThreadLocal<JwtToken> TOKEN = new InheritableThreadLocal<>();

    static {
        MAP.put(TOKEN_OBJECT, TOKEN);
    }

    public static JwtToken getToken() {
        Object o = MAP.get(TOKEN_OBJECT).get();
        if (o == null) {
            return null;
        }
        return (JwtToken) o;
    }
    ...
}

```

