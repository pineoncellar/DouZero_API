# DouZero_API

### API 交互斗地主 AI

<img width="500" src="https://gitee.com/daochenzha/DouZero/raw/main/imgs/douzero_logo.jpg" alt="Logo" />

> 本项目基于[DouZero](https://github.com/kwai/DouZero)

## 调用API

> 程序默认运行于`24813`端口
> 目前只支持post方法调用，请求头 `Content-Type: application/json`

```json
{
  "action": string,
  "data": object
}
```

| 参数名 | 说明 |
|-----|---------|
| action | 上报类型，可选"init"/"play"，对应 初始化游戏/游戏进程上报 |
| data | 上报数据，见下方 |

上报数据：

### 初始化游戏

```json
{
  "pid": string / int,
  "three_landlord_cards": string,
  "ai_amount": int,
  "player_data":[
    {
      "model": string,
      "hand_cards": string,
      "position_code": int
    },
    {
      "model": string,
      "hand_cards": string,
      "position_code": int
    }
  ]
}
```

| 参数名 | 说明 | 示例 |
|-----|---------|--------|
| pid | 对局唯一标识，若为int类型会自动转为string | 10001 |
| three_landlord_cards | 三张地主牌 | "444" |
| ai_amount | AI玩家数量，为1或2 | 2 |
| player_data | AI玩家数据，AI玩家数为1时只会读取数组中的第一个元素，内容元素见下方 | \ |
| model | AI玩家使用的模型 | "WP" |
| hand_cards | AI玩家的手牌 | "333444456789TJQKA2XD" |
| position_code | AI玩家的位号 **0-地主上家，1-地主，2-地主下家** | 1 |

<details>
<summary>完整示例</summary>

```json
{
  "action": "init",
  "data": {
    "three_landlord_cards": "444",
    "pid": 10001,
    "ai_amount": 2,
    "player_data": [
      {
        "model": "WP",
        "hand_cards": "333444456789TJQKA2XD",
        "position_code": 1
      },
      {
        "model": "WP",
        "hand_cards": "3555666777888999T",
        "position_code": 2
      }
    ]
  }
}
```

</details>

### 游戏进程上报

也就是上报玩家出牌

```json
{
  "pid": string / int,
  "player": int,
  "cards": string
}
```

| 参数名 | 说明 | 示例 |
|-----|---------|--------|
| pid | 对局唯一标识，若为int类型会自动转为string | 10001 |
| player | 出牌玩家位号 | 0 |
| cards | 玩家出的牌，为空字符串则表示不要 | "TJQKA" |

> 程序并不会检测玩家所出的牌是否遵循规则，请保证上报数据准确

<details>
<summary>完整示例</summary>

```json
{
  "action": "play",
  "data": {
    "pid": 10001,
    "player": 0,
    "cards": "TJQKA"
  }
}
```

</details>

## API响应

```json
{
  "type": string,
  "action": string,
  "status": string,
  "msg": string,
  "data": object
}
```
| 参数名 | 说明 |
|-----|---------|
| type | 响应类型，与上报数据的`action`相对应，上报"play"时为"step" |
| action | 响应AI操作，尚未轮到AI出牌时为"receive"，AI出牌时为"play" |
| status | 响应状态，为"ok"/"fail" |
| msg | 错误信息，响应状态为"fail"时不为空 |
| data | 响应数据，见下方 |

响应数据：

```json
{
  "pid": pid,
  "game_over": boolen,
  "play": [
    {
      "cards": array,
      "confidence": string
    },
    {
      "cards": array,
      "confidence": string
    }
  ]
}
```

| 参数名 | 说明 |
|-----|---------|
| pid | 对应对局标识 |
| game_over | 对局是否结束，结束则为`true` |
| play | AI出牌数据，action为"receive"时无此元素，元素内容见下方 |
| cards | AI出的牌，为数组类型 |
| confidence | AI的胜率估计 |

## 预设模型简介

- WP

DouZero-WP (baselines/douzero_WP/): 以胜率（Winning Percentage, WP）为目标训练的Douzero智能体

- ADP

DouZero-ADP (baselines/douzero_ADP/): 以平均分数差异（Average Difference Points, ADP）为目标训练的Douzero智能体

> 大概更倾向于出炸弹刷分

## 自定义运行端口

程序默认运行于`0.0.0.0:24813`，通过`-H`参数修改host，`-p`参数修改端口，如：

```bash
DouZero_API.exe -H 127.0.0.1 -p 24814
```

```bash
python start.py -H 127.0.0.1 -p 24814
```

## 超时检测

程序每5分钟将检查一次进程列表，超过半个小时未响应的游戏进程将被删除。

## 使用自己的模型

在`baselines/`文件夹下新建文件夹，将自己训练的`landlord.ckpt`、`landlord_up.ckpt`、`landlord_down.ckpt`扔进去，文件夹名即为游戏初始化时需要填入的"model"参数

## 鸣谢
*   本项目基于[DouZero](https://github.com/kwai/DouZero)
*   借鉴了[DouZero_For_HappyDouDiZhu](https://github.com/tianqiraf/DouZero_For_HappyDouDiZhu)项目的部分代码与写法
