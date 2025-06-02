# DeepPath 标准 MCP API Curl 命令

## 获取可用函数列表

```bash
curl -X GET "https://deeppath.cc/api/mcp/standard" \
  -H "Authorization: Bearer dp_aea95abc22d9c360ecaecfe6a9f21e678388a6f7691befba"
```

## 获取项目信息

```bash
curl -X POST "https://deeppath.cc/api/mcp/standard" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dp_aea95abc22d9c360ecaecfe6a9f21e678388a6f7691befba" \
  -d '{
    "functionCall": {
      "name": "getProjectInfo",
      "parameters": {}
    }
  }'
```

## 获取任务列表

```bash
curl -X POST "https://deeppath.cc/api/mcp/standard" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dp_aea95abc22d9c360ecaecfe6a9f21e678388a6f7691befba" \
  -d '{
    "functionCall": {
      "name": "getTasks",
      "parameters": {
        "status": "all",
        "limit": 10
      }
    }
  }'
```

## 获取目标列表

```bash
curl -X POST "https://deeppath.cc/api/mcp/standard" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dp_aea95abc22d9c360ecaecfe6a9f21e678388a6f7691befba" \
  -d '{
    "functionCall": {
      "name": "getGoals",
      "parameters": {
        "includeCompleted": false
      }
    }
  }'
```

## 获取笔记列表

```bash
curl -X POST "https://deeppath.cc/api/mcp/standard" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dp_aea95abc22d9c360ecaecfe6a9f21e678388a6f7691befba" \
  -d '{
    "functionCall": {
      "name": "getNotes",
      "parameters": {
        "limit": 10
      }
    }
  }'
```

## 获取自动化规则

```bash
curl -X POST "https://deeppath.cc/api/mcp/standard" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dp_aea95abc22d9c360ecaecfe6a9f21e678388a6f7691befba" \
  -d '{
    "functionCall": {
      "name": "getAutomations",
      "parameters": {}
    }
  }'
```

## 任务相关操作

### 创建任务

```bash
curl -X POST "https://deeppath.cc/api/mcp/standard" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dp_aea95abc22d9c360ecaecfe6a9f21e678388a6f7691befba" \
  -d '{
    "functionCall": {
      "name": "createTask",
      "parameters": {
        "title": "测试任务",
        "description": "这是一个通过API创建的测试任务"
      }
    }
  }'
```

### 获取任务详情

```bash
curl -X POST "https://deeppath.cc/api/mcp/standard" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dp_aea95abc22d9c360ecaecfe6a9f21e678388a6f7691befba" \
  -d '{
    "functionCall": {
      "name": "getTask",
      "parameters": {
        "taskId": "任务ID"
      }
    }
  }'
```

### 更新任务

```bash
curl -X POST "https://deeppath.cc/api/mcp/standard" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dp_aea95abc22d9c360ecaecfe6a9f21e678388a6f7691befba" \
  -d '{
    "functionCall": {
      "name": "updateTask",
      "parameters": {
        "taskId": "任务ID",
        "title": "更新的任务标题",
        "description": "这是通过API更新的任务描述"
      }
    }
  }'
```

### 删除任务

```bash
curl -X POST "https://deeppath.cc/api/mcp/standard" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dp_aea95abc22d9c360ecaecfe6a9f21e678388a6f7691befba" \
  -d '{
    "functionCall": {
      "name": "deleteTask",
      "parameters": {
        "taskId": "任务ID"
      }
    }
  }'
```

## 目标相关操作

### 创建目标

```bash
curl -X POST "https://deeppath.cc/api/mcp/standard" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dp_aea95abc22d9c360ecaecfe6a9f21e678388a6f7691befba" \
  -d '{
    "functionCall": {
      "name": "createGoal",
      "parameters": {
        "title": "测试目标",
        "description": "这是一个通过API创建的测试目标",
        "isMainGoal": false
      }
    }
  }'
```

### 更新目标

```bash
curl -X POST "https://deeppath.cc/api/mcp/standard" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dp_aea95abc22d9c360ecaecfe6a9f21e678388a6f7691befba" \
  -d '{
    "functionCall": {
      "name": "updateGoal",
      "parameters": {
        "goalId": "目标ID",
        "title": "更新的目标标题",
        "description": "这是通过API更新的目标描述",
        "progress": 50
      }
    }
  }'
```

### 删除目标

```bash
curl -X POST "https://deeppath.cc/api/mcp/standard" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dp_aea95abc22d9c360ecaecfe6a9f21e678388a6f7691befba" \
  -d '{
    "functionCall": {
      "name": "deleteGoal",
      "parameters": {
        "goalId": "目标ID"
      }
    }
  }'
```

## 笔记相关操作

### 创建笔记

```bash
curl -X POST "https://deeppath.cc/api/mcp/standard" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dp_aea95abc22d9c360ecaecfe6a9f21e678388a6f7691befba" \
  -d '{
    "functionCall": {
      "name": "createNote",
      "parameters": {
        "title": "测试笔记",
        "content": "这是一个通过API创建的测试笔记内容"
      }
    }
  }'
```

### 更新笔记

```bash
curl -X POST "https://deeppath.cc/api/mcp/standard" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dp_aea95abc22d9c360ecaecfe6a9f21e678388a6f7691befba" \
  -d '{
    "functionCall": {
      "name": "updateNote",
      "parameters": {
        "noteId": "笔记ID",
        "title": "更新的笔记标题",
        "content": "这是通过API更新的笔记内容"
      }
    }
  }'
```

### 删除笔记

```bash
curl -X POST "https://deeppath.cc/api/mcp/standard" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dp_aea95abc22d9c360ecaecfe6a9f21e678388a6f7691befba" \
  -d '{
    "functionCall": {
      "name": "deleteNote",
      "parameters": {
        "noteId": "笔记ID"
      }
    }
  }'
```

## 自动化规则相关操作

### 创建自动化规则

```bash
curl -X POST "https://deeppath.cc/api/mcp/standard" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dp_aea95abc22d9c360ecaecfe6a9f21e678388a6f7691befba" \
  -d '{
    "functionCall": {
      "name": "createAutomation",
      "parameters": {
        "title": "测试自动化规则",
        "description": "这是一个通过API创建的测试自动化规则",
        "dueDateTime": "2023-12-31T23:59:59Z",
        "isRepeating": true,
        "repeatPattern": "weekly",
        "actionType": "notification"
      }
    }
  }'
```

### 更新自动化规则

```bash
curl -X POST "https://deeppath.cc/api/mcp/standard" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dp_aea95abc22d9c360ecaecfe6a9f21e678388a6f7691befba" \
  -d '{
    "functionCall": {
      "name": "updateAutomation",
      "parameters": {
        "automationId": "自动化规则ID",
        "title": "更新的自动化规则标题",
        "description": "这是通过API更新的自动化规则描述",
        "isRepeating": false
      }
    }
  }'
```

### 删除自动化规则

```bash
curl -X POST "https://deeppath.cc/api/mcp/standard" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dp_aea95abc22d9c360ecaecfe6a9f21e678388a6f7691befba" \
  -d '{
    "functionCall": {
      "name": "deleteAutomation",
      "parameters": {
        "automationId": "自动化规则ID"
      }
    }
  }'
```

## 日历事件相关操作

### 创建日历事件

```bash
curl -X POST "https://deeppath.cc/api/mcp/standard" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dp_aea95abc22d9c360ecaecfe6a9f21e678388a6f7691befba" \
  -d '{
    "functionCall": {
      "name": "createCalendarEvent",
      "parameters": {
        "title": "测试日历事件",
        "description": "这是一个通过API创建的测试日历事件",
        "startTime": "2023-12-31T10:00:00Z",
        "endTime": "2023-12-31T11:00:00Z",
        "location": "线上会议",
        "isAllDay": false
      }
    }
  }'
```

### 获取日历事件

```bash
curl -X POST "https://deeppath.cc/api/mcp/standard" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dp_aea95abc22d9c360ecaecfe6a9f21e678388a6f7691befba" \
  -d '{
    "functionCall": {
      "name": "getCalendarEvents",
      "parameters": {
        "startDate": "2023-12-01T00:00:00Z",
        "endDate": "2023-12-31T23:59:59Z"
      }
    }
  }'
```

### 更新日历事件

```bash
curl -X POST "https://deeppath.cc/api/mcp/standard" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dp_aea95abc22d9c360ecaecfe6a9f21e678388a6f7691befba" \
  -d '{
    "functionCall": {
      "name": "updateCalendarEvent",
      "parameters": {
        "eventId": "事件ID",
        "title": "更新的日历事件标题",
        "description": "这是通过API更新的日历事件描述",
        "location": "办公室会议室"
      }
    }
  }'
```

### 删除日历事件

```bash
curl -X POST "https://deeppath.cc/api/mcp/standard" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dp_aea95abc22d9c360ecaecfe6a9f21e678388a6f7691befba" \
  -d '{
    "functionCall": {
      "name": "deleteCalendarEvent",
      "parameters": {
        "eventId": "事件ID"
      }
    }
  }'
```

### 获取 ICS 链接

```bash
curl -X POST "https://deeppath.cc/api/mcp/standard" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dp_aea95abc22d9c360ecaecfe6a9f21e678388a6f7691befba" \
  -d '{
    "functionCall": {
      "name": "getIcsLink",
      "parameters": {}
    }
  }'
```

## 控制台灯

### 开关台灯

```bash
curl -X POST "https://deeppath.cc/api/mcp/standard" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dp_aea95abc22d9c360ecaecfe6a9f21e678388a6f7691befba" \
  -d '{
    "functionCall": {
      "name": "toggleLamp",
      "parameters": {
        "status": "on"
      }
    }
  }'
```

## 获取当前日期和时间

```bash
curl -X POST "https://deeppath.cc/api/mcp/standard" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dp_aea95abc22d9c360ecaecfe6a9f21e678388a6f7691befba" \
  -d '{
    "functionCall": {
      "name": "getCurrentDateTime",
      "parameters": {
        "format": "iso"
      }
    }
  }'
```
