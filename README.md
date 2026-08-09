# PFC 数值模拟数据文件集

> 本仓库收录基于 **Itasca PFC (Particle Flow Code)** 6.0 的二维（PFC2D）与三维（PFC3D）离散元数值模拟数据文件，涵盖教程示例、验证算例、工程应用及 Python 脚本接口等内容。

## 目录结构

```
pfc-code/
├── data/                          # 锚杆拉拔项目（自定义项目）
│   ├── 01_sample_build.dat         #   第1步：试样生成
│   ├── 02_add_anchor.dat           #   第2步：添加锚杆孔
│   ├── 03_bond.dat                 #   第3步：颗粒胶结
│   ├── 04_anchor_balls.dat         #   第4步：锚杆颗粒生成与刚性化
│   ├── 05_pullout.dat              #   第5步：拉拔加载
│   ├── 06_grout.dat                #   第6步：灌浆界面胶结
│   ├── 07_free_balance.dat         #   第7步：自由平衡
│   └── PFC建模要点.md              #   建模方法论与约定（长期记忆文档）
│
├── datafiles2d/                   # PFC2D 数据文件
│   ├── examples/                   #   示例
│   │   ├── granular/               #     颗粒材料双轴试验
│   │   ├── rocktest/               #     岩石力学测试
│   │   └── simplebbm/              #     简单块体模型
│   ├── python/                     #   Python 脚本
│   │   ├── basic_python/           #     Python 基础示例
│   │   └── gui_example/            #     GUI 示例
│   ├── thermal/                    #   热力学分析
│   │   └── transient_sheet/        #     瞬态热传导
│   ├── tutorials/                  #   入门教程
│   │   ├── attributes_and_properties/
│   │   ├── balls_in_a_box/
│   │   ├── fractured_rock/
│   │   ├── hopper/
│   │   ├── inclusions/
│   │   ├── joint_slip/
│   │   ├── shallow_foundation/
│   │   └── using_cmat/
│   └── verifications/              #   验证算例
│       ├── adhesive_rolling_resistance/
│       ├── burger/
│       ├── cantilever/
│       ├── measure_logic/
│       ├── rolling_resistance/
│       └── wave_propagation/
│
├── datafiles3d/                   # PFC3D 数据文件
│   ├── ccfd/                       #   CFD 耦合计算
│   │   ├── cylinder.gid/
│   │   ├── droptest1.gid/
│   │   ├── droptest2.gid/
│   │   ├── elbow.gid/
│   │   ├── fluidized_bed.gid/
│   │   ├── one_way_coupling/
│   │   └── porous1.gid/
│   ├── examples/                   #   工程示例
│   │   ├── buttress/               #     支挡结构
│   │   ├── dfn_generation/         #     离散断裂网络生成
│   │   ├── fragmentation/          #     破碎模拟
│   │   ├── hopper_flow/            #     料斗流动
│   │   ├── PunchIndentation/       #     冲头压痕
│   │   ├── ribbon_blender/         #     螺带混合器
│   │   ├── rockslide/              #     滑坡模拟
│   │   ├── rocktest/               #     岩石力学测试
│   │   ├── simplebbm/              #     简单块体模型
│   │   ├── SleevedTriaxialTest/    #     带套三轴试验
│   │   ├── SoftBonded/             #     软胶结模型
│   │   └── tunnelbbm/              #     隧道块体模型
│   ├── python/                     #   Python 脚本
│   │   ├── array_interface/
│   │   ├── basic_python/
│   │   ├── gui_example/
│   │   ├── python_pfc/
│   │   ├── test_ucs/
│   │   └── using_scipy/
│   ├── thermal/                    #   热力学分析
│   │   ├── constrained_expansion/  #     约束膨胀
│   │   └── free_expansion/         #     自由膨胀
│   ├── tutorials/                  #   入门教程
│   │   ├── attributes_and_properties/
│   │   ├── balls_in_a_box/
│   │   ├── bonded_assembly/
│   │   ├── callbacks/
│   │   ├── clumps_in_a_box/
│   │   ├── fractured_rock/
│   │   ├── hopper/
│   │   ├── joint_slip/
│   │   ├── shallow_foundation/
│   │   ├── size_distribution/
│   │   └── table_tennis/
│   └── verifications/              #   验证算例
│       ├── adhesive_rolling_resistance/
│       ├── array_strength/
│       ├── burger/
│       ├── cantilever/
│       ├── hertz_model/
│       ├── measure_logic/
│       ├── restitution/
│       ├── rolling_resistance/
│       ├── Settle/
│       ├── sliding-wedge/
│       ├── Wave/
│       └── wave_propagation/
│
├── .gitignore
└── README.md
```

## 文件类型说明

| 扩展名 | 说明 |
|--------|------|
| `.p3dat` / `.p2dat` | PFC3D / PFC2D 命令数据文件（主脚本） |
| `.p3prj` / `.p2prj` | PFC3D / PFC2D 项目文件 |
| `.f3dat` | FLAC3D 命令文件（用于 PFC-FLAC 耦合） |
| `.f3prj` | FLAC3D 项目文件 |
| `.dat` | 通用 PFC 命令文件 |
| `.prj` | 通用项目文件 |
| `.p3fis` / `.p2fis` / `.fis` | FISH 语言脚本文件 |
| `.py` | Python 脚本（PFC Python 接口） |
| `.stl` | STL 几何文件（导入三维几何体） |
| `.inp` | 输入配置文件 |
| `.md` | 文档文件 |

## 主要内容

### `data/` — 锚杆拉拔数值试验项目

一个完整的锚杆拉拔离散元模拟项目，按 save/restore 链分步执行：

| 步骤 | 文件 | 说明 |
|:----:|------|------|
| 1 | `01_sample_build.dat` | 建立立方体试样（50×50×50），生成颗粒、初始平衡 |
| 2 | `02_add_anchor.dat` | 生成圆柱锚杆孔墙体、删除孔内颗粒 |
| 3 | `03_bond.dat` | 重定义 CMAT 并施加平行胶结（linearpbond） |
| 4 | `04_anchor_balls.dat` | 生成锚杆颗粒列、刚性化胶结、删除锚杆墙与出口边界 |
| 5 | `05_pullout.dat` | 固定锚固端、施加拉拔力、监测位移与反力 |
| 6 | `06_grout.dat` | 胶结锚杆-岩石界面（模拟灌浆粘结） |
| 7 | `07_free_balance.dat` | 释放约束、系统自由平衡 |

建模方法论详见 [`data/PFC建模要点.md`](data/PFC建模要点.md)。

### `datafiles2d/` — PFC2D 数据文件

- **examples**：颗粒材料双轴试验（granular）、岩石力学测试（rocktest）、简单块体模型（simplebbm）
- **python**：Python 基础语法与 GUI 示例
- **thermal**：瞬态热传导分析
- **tutorials**：8 个入门教程，涵盖基础概念（CMAT、属性、胶结、断裂等）
- **verifications**：6 类验证算例（滚动阻力、Burger 模型、悬臂梁、波传播等）

### `datafiles3d/` — PFC3D 数据文件

- **ccfd**：CFD-DEM 耦合计算（圆柱绕流、流化床、多孔介质、单向耦合等）
- **examples**：12 个工程应用示例（滑坡、隧道、三轴试验、混合器、DFN 等）
- **python**：6 个 Python 接口示例（数组接口、SciPy 集成、UCS 测试等）
- **thermal**：热-力耦合分析（约束膨胀、自由膨胀）
- **tutorials**：11 个入门教程（含乒乓球游戏等趣味示例）
- **verifications**：12 类验证算例（Hertz 接触、恢复系数、滑动楔体、波传播等）

## 技术要点

### 接触模型

本仓库涉及的主要接触模型：

| 模型 | 用途 |
|------|------|
| `linear` | 线性接触模型（成样、非胶结阶段） |
| `linearpbond` | 平行胶结模型（岩石、锚杆、灌浆胶结） |
| `hertz` | Hertz 接触模型（验证算例） |
| `burger` | Burger 粘弹性模型（应力松弛） |
| `adhesive_rolling_resistance` | 粘附滚动阻力模型 |

### CMAT 规范

- 组内接触（两端同组）：`range group '<组名>' match 2`
- 跨组界面（两端分属两组）：`range fish @<自定义函数>`
- 球-墙接触刚度取球-球的 3 倍（`emod_facet = 3 × emod_lin`）
- 刚度用 `method deform emod/kratio` 定义，不直接写 `kn/ks`

### Python 接口

PFC 内置 Python 解释器，支持通过 Python 脚本：
- 访问模型变量与 FISH 变量
- 使用 NumPy / SciPy 进行数据处理
- 实现自定义 GUI 界面
- 数组接口实现 PFC 数据与 NumPy 交互

## 使用方法

1. 安装 PFC 6.0（或更高版本）
2. 打开对应的项目文件（`.p3prj` / `.p2prj`）或直接 `call` 数据文件
3. 按步骤执行（对于 `data/` 下的锚杆项目，按 01→07 顺序执行）

```pfc
; 示例：在 PFC3D 中运行教程
call 'datafiles3d/tutorials/balls_in_a_box/cmlinear_simple.p3dat'
```

## 相关链接

- [Itasca 官网](https://www.itascacg.com/)
- [PFC 在线文档](https://docs.itascacg.com/pfc/)
- [PFC 论坛](https://forum.itascacg.com/)

## 许可声明

本仓库为学习与研究用途。PFC 相关文件内容基于 Itasca PFC 软件命令体系编写，PFC 软件版权归 Itasca Consulting Group 所有。
