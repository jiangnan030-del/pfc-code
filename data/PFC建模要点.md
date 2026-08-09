# PFC 建模要点（长期记忆草稿）

> 记录用户进行 PFC 6.0 数值试验时的建模约定与方法论，便于后续项目复用。
> 由 2026-08-08 的对话整理。

## 1. 数值参数统一用 Fish 变量
- 尺寸、粒径、孔隙率、刚度、胶结强度等所有数值参数，都定义为 Fish 变量（写在脚本顶部），便于批量修改与参数扫描。
- 例：`[sample_half=25.0]`、`[radius_min=2.0]`、`[radius_max=3.0]`、`[porosity=0.3]` 等。
- 命令中通过 `[变量名]` 内联调用。

## 2. 胶结时机：形状边界确定之后
- 松散颗粒通过胶结形成坚硬材料，**一般在试样形状/边界最终确定后再施加胶结**（如删完锚杆孔/开挖之后）。
- 施加胶结三步法（标准写法）：
  1. **定义接触（重定义所有接触）**：先用 `contact cmat default type ball-ball ...` 与 `type ball-facet ...` 写完整默认接触表（含胶结模型与参数），然后**用 `contact cmat apply` 对所有已存在接触按新 CMAT 重定义**（球-球→linearpbond（默认胶结模型）、球-墙→linear）。
     - ⚠️ 不要用逐条 `contact model linearpbond range contact type 'ball-ball'` 手动指派——`contact cmat apply` 一步把整张表应用到所有接触，更不容易漏配参数。
     - ⚠️ 接触模型必须由 CMAT（`contact cmat default` / `contact cmat add`）定义，**不能只用 `contact property` 设定模型**。按颗粒组分给不同接触时，用 `contact cmat add <id> ... range group '<组>'` **直接以颗粒组界定**，并**不要把 `type` 关键字与 `range group` 混用**——即同一条目里不要既写 `type ball-ball` 又写 `range group 'X'`（`type` 等价于 `range contact type 'ball-ball'`，叠加 `range group` 会覆盖类型过滤、误匹配 ball-facet）。球-墙(ball-facet) 仍用 `contact cmat default type ball-facet`（emod=3×）单独界定。
    - **规范写法（本项目：试样 shiyang 用 `id 1`、锚杆 anchor_ball 用 `id 2`、锚杆-岩石界面用 `id 3`，各自独立界定）**：
      - **组内接触（两端都属同一组）用 `range group '<组>' match 2`**：`match 2` = 两端都命中该组，无需自定义 FISH 函数，比 `range fish` 更简洁。试样内(id 1)、锚杆内(id 2) 都属此类：
        ```
        contact cmat add   1 model linearpbond ...
            method deform emod [emod_lin] kratio [kratio_lin] ...
            pb_deform emod [pb_emod] kratio [pb_kratio] ...
            property pb_ten [pb_ten] pb_coh [pb_coh] pb_fa [pb_fa] lin_mode 1 ...
            range group 'shiyang' match 2
        contact cmat add   2 model linearpbond ...
            method deform emod [emod_lin] kratio [kratio_lin] ...
            pb_deform emod [pb_emod] kratio [pb_kratio] ...
            property pb_ten [pb_ten_anchor] pb_coh [pb_coh_anchor] pb_fa [pb_fa_anchor] lin_mode 1 rgap [rgap] ...
            range group 'anchor_ball' match 2
        ```
      （刚度由 `method deform`/`pb_deform` 用 emod/kratio 自动求 kn/ks、pb_kn/pb_ks；`property` 仅给强度与 `lin_mode 1`；相切颗粒需加极小 `rgap`，见下条）
      - **跨组界面（两端分属两组，如锚杆-岩石界面）用 `range fish @<sfunc>`**：`match 2` 无法表达“一端 A、一端 B”，必须用 `range fish`。FISH 函数须定义为 `fish define <sfunc>(pos, c)`（PFC 传入元素位置与接触指针 `c`，返回布尔）；⚠️ **调用语法 `range fish @<sfunc>`（函数名前必须加 `@`）**，FISH 逻辑运算符用 `&`（与）/`|`（或），**不要写 `and`/`or`**（非 FISH 运算符，写了会语法错误）。本项目第6步用 `is_grout` 判“一端 shiyang、一端 anchor_ball”：
        ```
        fish define is_grout(pos, c)
            is_grout = false
            if type.pointer.id(c) == contact.typeid('ball-ball')
                local b1 = contact.end1(c)
                local b2 = contact.end2(c)
                if (ball.isgroup(b1,'shiyang')    & ball.isgroup(b2,'anchor_ball')) | ...
                   (ball.isgroup(b1,'anchor_ball') & ball.isgroup(b2,'shiyang'))
                    is_grout = true
                endif
            endif
        end
        contact cmat add   3 model linearpbond ...
            method deform emod [emod_grout] kratio [kratio_grout] ...
            pb_deform emod [pb_emod_grout] kratio [pb_kratio_grout] ...
            property pb_ten [pb_ten_grout] pb_coh [pb_coh_grout] pb_fa [pb_fa_grout] lin_mode 1 rgap [rgap] ...
            range fish @is_grout
        ```
    - ⚠️ **组内/跨组筛选规则**：组内（两端同组）用 `range group '<组>' match 2` 即可；跨组（两端分属两组）`match 2` 无能为力，必须用 `range fish @<sfunc>`。
      - 注意：对 `contact` 命令用 `range group '<组>'`（无 match）检查的是**接触组**（非颗粒组）、用 `range ball group '<组>'` 语义是“任一端点属于该组”——二者都不能精确表达“两端分属两组”，故跨组界面必须用 `range fish`。
    - ⚠️ **跨组界面（id 3）用 `range fish @is_grout` 精确命中**：组内条目（id 1/2，均 `match 2`）只命中“组内”接触后，所有“跨组”接触（一端 shiyang、一端 anchor_ball，如本项目锚杆-岩石界面）会被漏掉。本项目第6步用 `id 3` + `range fish @is_grout` 把该界面胶结为浆液粘结：
      ```
      contact cmat add   3 model linearpbond ...
          ...
          range fish @is_grout
      ```
      （注：本项目第6步中锚杆-岩石界面此前由 `cmat default type ball-ball model linear` 承接为不胶结的线性接触；重定义 CMAT 后先 `contact cmat apply range fish @is_grout`（仅界面重套用，岩石/锚杆模型不变故既有胶结保留，仅界面被重赋为 id 3 的 linearpbond），再用 `contact method bond gap range fish @is_grout` 施胶，不碰岩石/锚杆内部已胶结接触。相比“match 2 + id 3 兜底 + Fish 打标 group”的旧做法，range fish 一步到位、无打标丢失风险。）
     - ⚠️ 相切/紧挨的颗粒（gap≈0）直接胶结时，浮点存储误差可能导致接触激活失败、bond 失效；解决办法是在 ball-ball linearpbond 的接触参数里加一个**极小正值参考间隙 `rgap`**（如 `1e-5`），使这类接触稳定激活并可成功胶结（活动距离 `getActivityDistance` = rgap）。
  2. **接触力与速度清零**：消除成样/删颗粒过程残留的力与速度。
     - 接触线性力清零：`contact property lin_force 0 0 0`（**不是** `contact reset forces`）。
     - 颗粒合力清零：`ball attribute force-contact multiply 0 moment-contact multiply 0`（同时清掉接触与颗粒上的残余力/力矩；**不是** `ball attribute force multiply 0`）。
     - 速度清零：`model calm`（**不是** `ball initialize velocity (0,0,0)`）。
  3. **施加胶结**：`contact method bond gap <值> range contact type 'ball-ball'` 对 gap 小于阈值的球-球接触生成胶结。
- 胶结后建议 `model cycle 1` 再 `model solve` 稳定。

## 3. 成样阶段：线性接触模型，不给摩擦 fric
- 第一步成样（制样）时，分别用 `contact cmat default type ball-ball` 与 `type ball-facet`（球-墙）设定 `model linear`，**不设置 fric**（摩擦系数在后续阶段或胶结后再给）；颗粒-墙体接触刚度取颗粒间 3 倍（见第 9 节）。
- 目的：让松散颗粒先自由堆积、排气，避免过早产生摩擦约束。

## 4. 初始重叠处理流程
- `model cycle 2000 calm 50`：主要作用是消除颗粒初始大重叠产生的过大速度（calm 每 50 步清零速度）。
- 该步之后，**删除试样边界（盒）以外的颗粒**，清理越界/杂散颗粒，保证边界干净。
  - ⚠️ **`range` 中没有 `box` 关键字**，不能用 `ball delete range box ... not`。
  - 正确做法：在三维度分别用 `pos-x`/`pos-y`/`pos-z` + `not` 删除任一分量落在盒外的颗粒（三条命令并列，等效“盒外”）：
    - `ball delete range pos-x -25 25 not`
    - `ball delete range pos-y -25 25 not`
    - `ball delete range pos-z -25 25 not`
- 然后再用 `model solve` 求解到力学平衡（而非仅 cycle）。

## 5. 成样用 ball distribute 而非 ball generate
- 默认不用 `ball generate`；用 `ball distribute` 生成指定密实度的颗粒。
- `ball distribute porosity 0.3 radius <rmin> <rmax> box ...`（默认孔隙率即为 0.3，可指定）。

## 6. 删除指定范围内颗粒：优先 ball delete range
- 删除某几何范围内的颗粒，一般用 `ball delete range` 直接指定范围，**圆柱形范围用 `range cylinder`**。
- 圆柱范围语法（与 wall generate 不同！）：
  - `ball delete range cylinder end-1 (x1,y1,z1) end-2 (x2,y2,z2) radius <r>`
  - 注意：range 用 `end-1`/`end-2`（轴线两端点）+ `radius`；
  - 而 `wall generate cylinder` 用 `base`/`axis`/`height`/`radius`。二者关键字不同。
- ⚠️ `wall generate cylinder` 的**关键字顺序**有讲究（实测，顺序错会报错）：
  - `id`/`name`/`group` 是 `wall generate` 的**主关键字**，必须写在 `cylinder` 等形状关键字**之前**；`one-wall` 等是形状子关键字，写在 `cylinder` 之后。
  - 正确：`wall generate name 'anchor' group 'anchor' cylinder base <v> axis <v> height <f> radius <f> cap true one-wall`
    （`name`/`group` 在前，`cylinder` 在中，`cap true` 写在最后；`one-wall` 让侧面与两端端盖同属一个 wall，便于后续按 name 删除）
  - 错误：`wall generate cylinder base ... axis ... height ... radius ... cap false group 'anchor'`
    （`group` 放在 `cylinder` 之后会报错；且 `cap false` 会让圆柱两端开口，端部邻近颗粒沿轴线漏进空腔）
- ⚠️ `wall generate group 'anchor' ...` 中的 `group` 是赋给生成的 **facet**（面片），不是赋给 wall 本身。若要按墙体删除，应同时用 `name '...'` 给 wall 命名，再用 `wall delete walls range name '...'`。
- 例：`ball delete range cylinder end-1 (-20,0,0) end-2 (30,0,0) radius 2.0`（本项目锚杆半径 2.0；range 用 end-1/end-2/radius）
- 也可用 `not` 取反（删除圆柱“之外”的颗粒）。
- ⚠️ 补充：删除“盒外”颗粒时 `range` 没有 `box` 关键字，必须用 `pos-x`/`pos-y`/`pos-z` + `not` 在三维度分别删除（见第 4 节），不能写 `range box ... not`。

## 7. 结果文件管理：每步 solve 后 save，下一步先 restore
- 每个阶段运行到 `model solve` 平衡后，都应 `model save` 一个独立的结果文件（.sav）。
- 下一个阶段开始时，**首先 `model restore` 上一步保存的结果文件**，再继续往下做。
- 胶结作为一个独立阶段，单独保存一个 sat 文件（例如 `sample_bonded`）。
- 好处：形成清晰的“存档链”，便于断点续算、参数回溯、单独复现或替换某一步。

### 本项目（锚杆拉拔）文件组织（按 save/restore 链拆分）
| 文件 | 起始动作 | 关键操作 | 结束存档 |
|------|----------|----------|----------|
| `01_sample_build.dat` | `model new` | 先 `model domain -25 25`；建 6 个独立命名平面墙（`wall generate name <n> plane position <v> dip <a> dip-direction <a>`，name 必须在 plane 前，平面截断于 domain ±25）→ 扩 domain 至 ±40 容纳锚杆 → CMAT（ball-ball/ball-facet 均 `method deform` 用 emod/kratio 定义刚度，墙 emod=3×；成样阶段**不加** lin_mode 1）→ `ball distribute`（porosity 0.3，半径 2~3）→ `cycle 2000 calm 50` → 删盒外颗粒（pos-x/y/z + not）→ `model solve` | `model save 'sample_built'` |
| `02_add_anchor.dat` | `model restore 'sample_built'` | `wall generate name 'anchor' group 'anchor' cylinder ... one-wall`（base/axis/height/radius，cap true 保留端盖；name/group 在前、cap 在后、one-wall 让各面同属一个 wall）→ `model cycle 2000 calm 50`（去插入 wall 的初始重叠）→ `ball delete range cylinder`（end-1/end-2/radius）→ `model solve` | `model save 'sample_anchored'` |
| `03_bond.dat` | `model restore 'sample_anchored'` | 重定义 CMAT（按颗粒组分别界定，接触类型写在 range 内）：球-墙→linear（emod=3×，`lin_mode 1`）；球-球默认兜底→linearpbond（`method deform`+`method pb_deform` 用 emod/kratio，均 `lin_mode 1`，含极小 `rgap`）；**试样(shiyang)球-球 → `cmat add id 1` 按组单独指定**（`range group 'shiyang' match 2`）→ `contact cmat apply` → 清零力（`contact property lin_force 0 0 0` + `ball attribute force-contact multiply 0 moment-contact multiply 0`）→ `model calm` → `contact method bond gap`（gap=radius_min）→ `model cycle 1` → `model solve` | `model save 'sample_bonded'` |
| `04_anchor_balls.dat` | `model restore 'sample_bonded'` | 先 `cmat add id 2` 用 `range group 'anchor_ball' match 2` 精确界定锚杆内接触（两端都 anchor_ball，含极小 `rgap`、锚杆专用强度）；球-球默认 `cmat default type ball-ball model linear`（不胶结）承接锚杆-岩石界面；Fish 沿 x 轴生成一行锚杆颗粒（半径=0.8×墙半径、y=z=0、x 首粒=x0+1.2R、递增=直径、超圆柱为止，分组 anchor_ball）→ `wall delete walls range name 'anchor'`（删圆柱墙）+ `wall delete walls range name 'face_xp'`（删 +x 面，拉拔出口；其余 5 面保留）→ `model cycle 2000 calm 50`（让新接触被检测、清初速度）→ 用 `range group 'anchor_ball' match 2` 直接对锚杆-锚杆接触 `contact cmat apply` + `contact method bond gap` 施胶（刚性杆体，**无需打标 group**；锚杆专用强度/rgap 由 cmat add id 2 定义、不再用 contact property 覆盖，**不胶结锚杆-岩石界面**；界面由球-球默认 linear 承接，待第6步胶结）→ `model solve` | `model save 'sample_anchor'` |
| `05_pullout.dat` | `model restore 'sample_anchor'` | 拉拔参数（`pull_force` 占位值、`pull_ratio`）；`ball fix velocity` + `ball fix spin` 固定锚固颗粒 `anchor_id_anchor`（首粒，岩内锚固端）；Fish 记录拉拔颗粒 `anchor_id_pull` 初始 x；`ball attribute force-applied-x [pull_force]` 对拉拔/张拉颗粒施加向外(+x)力 → 经刚性杆体传导；`history fish` 监测拉拔位移 `pull_disp_func` 与锚固端反力 `anchor_rx_func` → `model solve ratio`（持续拔出不收敛则改用 `model cycle`） | `model save 'sample_pullout'` |
| `06_grout.dat` | `model restore 'sample_pullout'` | 重定义 CMAT（cmat add 规范，建立在 05 pullout 之上、线性递进）：球-墙→linear（emod=3×）；id 1 `range group 'shiyang' match 2`（组内）、id 2 `range group 'anchor_ball' match 2`（组内）、id 3 `range fish @is_grout` 精确命中锚杆-岩石界面（一端 shiyang、一端 anchor_ball）；`contact cmat apply range fish @is_grout`（仅界面重套用为 id 3 的 linearpbond，不扰动已胶结的岩石/锚杆内部）→ 清零力/速度 → `contact method bond gap range fish @is_grout`（仅胶结界面，不碰岩石/锚杆内部已胶结接触）→ `model solve` | `model save 'sample_grout'` |
| `07_free_balance.dat` | `model restore 'sample_grout'` | 用 `ball free velocity` + `ball free spin` 解除颗粒约束（释放此前 `ball fix` 固定的锚固颗粒等，不加 range 作用于全体，边界约束由 6 面墙体提供）→ （可选）清零 `force-applied` → `model solve ratio-average [free_ratio]` 重新平衡 | `model save 'sample_freed'` |

> 注：圆柱 **wall** 用 `base`/`axis`/`height`/`radius`（且 `group` 写在 `cylinder` 前、`cap true` 写在最后，保留端盖以防端部颗粒漏入空腔）；圆柱 **range**（删颗粒）用 `end-1`/`end-2`/`radius`，二者关键字不同。

## 8. 删除某区域颗粒的标准流程（通用做法）
- 当需要删除“某个几何区域内”的颗粒（为锚杆孔、孔洞、开挖等预留空间）时，标准流程如下：
  1. **生成与删除边界一致的墙体**：先用 `wall generate` 生成一个贴合该区域的 wall（如本项目的圆柱体 `wall generate name 'anchor' group 'anchor' cylinder ... one-wall`）。该 wall 在几何上代表“要挖掉区域的边界”，不一定都是最终结构（锚杆孔时它正好就是锚杆界面）。给 wall 命名（`name`）便于后续按名删除。
  2. **`model cycle 2000 calm 50` 去除初始重叠**：新插入的 wall 会与周边已有颗粒发生初始重叠，产生异常大的速度/力。先 cycle+calm 把这部分初始重叠速度清零、系统初步松弛。
  3. **删除该区域内的颗粒**：`ball delete range ...`（圆柱用 `range cylinder end-1/end-2/radius`，见第 6 节）删除 wall 所包围范围内的颗粒，预留出空间。
  4. **`model solve` 平衡**：删颗粒后系统失去平衡，求解到新的力学平衡。
- 核心套路：**“先造边界 wall → 清初始重叠 → 删颗粒 → 平衡”**，适用于任何“挖洞/留孔/分区删除”场景，不局限于圆柱体。
- 本项目落地见 `02_add_anchor.dat`：先生成圆柱锚杆 wall → `model cycle 2000 calm 50` → `ball delete range cylinder` → `model solve`。

## 9. 默认接触参数需区分 ball-ball 与 ball-facet（墙体刚度取 3 倍）
- 定义默认接触（成样阶段的 `contact cmat default`）时，必须**分别**指定球-球（ball-ball）与球-墙（ball-facet）两类接触的参数，不能只给一个笼统的默认值（否则墙侧接触会丢失正确刚度甚至报错）。
  - ⚠️ PFC 中颗粒与墙体的接触类型是 **`ball-facet`**（墙由 facet 构成），不是 `ball-wall`，务必写对类型关键字。
- 约定：**颗粒-墙体接触刚度 = 颗粒-颗粒接触刚度 × 3**（即 `kn_facet = 3*kn_lin`、`ks_facet = 3*ks_lin`）。
  - 原因：墙体是刚性边界，相对颗粒更“硬”；墙侧接触刚度取高值可避免颗粒在边界处过度嵌入/软化，更接近真实刚性边界。
- 写法（成对定义，用 emod/kratio 而非 kn/ks）：
  - `contact cmat default type ball-ball model linear method deform emod [emod_lin] kratio [kratio_lin]`
  - `contact cmat default type ball-facet model linear method deform emod [emod_facet] kratio [kratio_facet]`
- 胶结阶段（`03_bond.dat`）同理：球-球改为 linearpbond（默认胶结模型）时，球-墙接触保持 linear 且有效模量仍取 3 倍（墙体不参与胶结），需显式保留/定义 ball-facet 条目；并通过 `contact cmat apply` 让球-墙与球-球接触一并按新 CMAT 重定义，否则墙侧接触会丢失正确刚度。

## 10. 接触刚度：kn/ks 与 emod/kratio 数学等价，二者只需定义其一
- **核心概念**：接触上真正起作用的是 `kn`（法向刚度）与 `ks`（切向刚度）。`emod`（有效模量）与 `kratio`（法向/切向刚度比）本质上是**计算 kn/ks 的方法**——PFC 会依据接触局部几何（接触面积、代表长度、最小半径等）由 `emod` 和 `kratio` 自动反算 `kn`、`ks`。因此 **kn/ks 与 emod/kratio 只需确定其中一对**，不要两对都写（都写既冗余又可能因数值不一致引入隐患）。
- **约定写法**：
  - 线性部分（linear / linearpbond 的线性段）：用 **`method deform emod <v> kratio <v>`** 定义刚度。
  - 平行粘结（胶结）部分：用 **`method pb_deform emod <v> kratio <v>`** 定义胶结刚度（自动求 `pb_kn`/`pb_ks`）。
  - 在 `contact cmat default` 中，把这两句 `method` 与 `property`（仅强度参数 pb_ten/pb_coh/pb_fa）并列即可，不要再在 `property` 里写 `kn/ks/pb_kn/pb_ks`。
- 例（03_bond.dat 球-球 linearpbond）：
  - `contact cmat default type ball-ball model linearpbond ...`
  - `method deform emod [emod_lin] kratio [kratio_lin] ...`（线性段）
  - `method pb_deform emod [pb_emod] kratio [pb_kratio] ...`（胶结段）
  - `property pb_ten [pb_ten] pb_coh [pb_coh] pb_fa [pb_fa]`（强度）
- ⚠️ “墙刚度 = 颗粒间 3 倍”这条约定（见第 9 节），在改用 emod/kratio 后体现为：**球-墙的有效模量 `emod_facet = 3 × emod_lin`**（kratio 取同值）。由于 ball-facet 与 ball-ball 的几何因子略有差异，这给出的是“约 3 倍”的等效刚度，方向一致。
- ⚠️ 命令关键字：`method deform` / `method pb_deform` 在 CMAT 定义时可用（部分写法/版本也写作 `deformability` / `pb_deformability`，二者等价）。
- **线性接触用 `lin_mode 1` 改为增量模型（仅胶结阶段）**：在胶结阶段所有定义线性段的接触（ball-facet 的 linear、linearpbond 的线性段）的 `property` 中加 `lin_mode 1`，将线性部分设为**增量模型**（相对默认的总量模型，增量模型更适合循环加载/卸载、避免力累积偏差）。**成样阶段（01_sample_build.dat）不加 `lin_mode 1`**——成样用总量模型即可，增量模型只在胶结时才启用。
- **胶结间隙 `bond_gap` 一般取最低颗粒粒径**：本项目 `bond_gap = radius_min`（即颗粒最小半径 2.0），可桥接微小间隙、让贴合与近贴合接触都参与胶结；取 `0` 则仅胶结完全贴合的接触。

## 11. 锚杆颗粒生成（第四步：用一行球代替圆柱锚杆 wall）
- 圆柱锚杆 wall 仅用于“占位/留孔”，最终要用一排颗粒组成的**锚杆杆体**代替它。锚杆颗粒沿圆柱轴线（本项目即 x 轴，y=z=0）排成**一行**。
- 锚杆颗粒半径：`anchor_radius = 0.8 × 圆柱 wall 半径`（本项目 wall 半径 2.0 → 锚杆颗粒半径 1.6），这样比试样颗粒（半径 2~3）小，可避免与试样颗粒重叠；且 < 圆柱半径，能整体落在孔内。
- 排布（Fish 批量生成）：
  - 每个颗粒 y、z 相同（都在轴线上），x 递增；
  - **递增距离 = 锚杆颗粒直径（2×半径）**，即相邻颗粒相切；
  - **第一个颗粒圆心** = 圆柱最左端 x（锚固端，`anchor_base` 的 x，本项目 -20）+ `0.2×半径` + `1×半径`（即 `+1.2×radius`）；
  - 循环生成，直到圆心 x **超过圆柱范围（拉拔端 x=base+height，本项目 30）为止**。
- 生成后给锚杆颗粒一个分组（如 `group 'anchor_ball'`），便于后续整体施加位移（拉拔）或单独赋密度/参数。
- ⚠️ **记录首尾两颗粒 id（已落地于 04）**：在生成 Fish 中把首颗粒（岩内锚固端 x0 侧）id 记到全局变量 `anchor_id_anchor`（锚固颗粒）、尾颗粒（自由拉拔端 x1 侧）id 记到全局变量 `anchor_id_pull`（拉拔颗粒），供第五步**固定锚固端速度/约束**、**对拉拔端施加拉拔速度或力**时直接引用（`ball fix velocity / ball attribute ... range id <id>` 等）。起始 id 用 900001，故锚固颗粒 id = 900001、拉拔颗粒 id 视生成数量而定（脚本 `io.out` 会打印二者）。
- 本步**删除圆柱墙体 + 锚杆这一侧(+x)的边界墙体**：因要在 04 单独删 +x 面，01 已把边界建成 6 个**独立命名平面墙**（`face_xn/yn/yp/zn/zp`），02 的圆柱墙也已命名（`name 'anchor'`），故 04 直接 `wall delete walls range name 'anchor'`（删圆柱墙）+ `wall delete walls range name 'face_xp'`（删 +x 面），拉拔端(x>25)可自由穿出；其余 5 面保留继续约束岩石。
- ⚠️ `wall delete` 默认删除 **facet**，要删除**墙体本身**必须加 `walls` 关键字：`wall delete walls range name '...'`。
- ⚠️ `wall generate plane` 正确关键字是 `name <n> plane position <点> dip <倾角> dip-direction <方位角>`，**不是** `origin`/`normal`；且 `name` 必须放在 `plane` 之前。平面墙会截断在 `model domain` 边界，故 01 生成平面时先把 domain 设为 ±25（平面即落在试样边界），随后再扩到 ±40 容纳锚杆拉拔端（已生成墙几何不变）。
- ⚠️ **刚性锚杆（已实现于 04 内）**：锚杆颗粒仅相切接触相连，受拉会散开，故在本步把它们胶结成刚性杆体。做法：用 `range group 'anchor_ball' match 2`（cmat add id 2 已用它界定“两端都属 anchor_ball”的锚杆内接触）直接对锚杆-锚杆接触施胶——锚杆专用强度/rgap 已在 `cmat add id 2`（`range group 'anchor_ball' match 2`）定义，故施胶段只 `contact cmat apply range group 'anchor_ball' match 2` + `contact method bond gap range group 'anchor_ball' match 2`，**无需先遍历打标 `anchor_internal` group**（避免重建接触丢失组标记）、**不再用 `contact property` 覆盖强度**（符合 cmat add 规范）。这样**只胶结锚杆颗粒之间，不胶结锚杆-岩石界面**（界面由 `cmat default type ball-ball model linear` 承接为线性接触，可传力不粘连；第6步再用 `id 3`（`range fish @is_grout`）把该界面胶结为浆液粘结）。
  - ⚠️ 接触模型必须由 CMAT 显式定义（不能仅靠 `contact property`）。按颗粒组分给不同接触时：**组内（两端同组）用 `range group '<组>' match 2`、跨组（两端分属两组）用 `range fish @<sfunc>`**（FISH 函数收 `(pos, 指针)`、返回布尔，显式判两端组归属；⚠️ 函数名前必须加 `@`、逻辑运算符用 `&`/`|` 不要写 `and`/`or`）；也**不要把 `type` 关键字与 `range group` 混用**（写成 `type ball-ball ... range group 'X'` 会覆盖类型过滤、误匹配 ball-facet）。本项目：试样(shiyang)用 `cmat add id 1`、`range group 'shiyang' match 2`；锚杆(anchor_ball)在 04 用 `cmat add id 2`、`range group 'anchor_ball' match 2`（均判“两端都属该组”）；界面在 06 用 `cmat add id 3`、`range fish @is_grout`（判“一端 shiyang、一端 anchor_ball”）；球-墙(ball-facet)仍用 `cmat default type`（emod=3×）；球-球默认兜底 `cmat default type ball-ball model linear`（不胶结）承接锚杆-岩石界面，第6步再由 id 3 把该界面胶结为浆液粘结。这样试样与锚杆各自有独立的 CMAT 条目，界面在第6步前保持线性、不粘连。
  - ⚠️ 不能直接用 `contact method bond gap ... range ball group 'anchor_ball'`：该范围语义是“**任一端点属于该组**”，会把锚杆-岩石接触也选入、误把锚杆与围岩粘死；也不能用 `range group 'anchor_ball'` 对接触下范围（检查的是接触组而非颗粒组，匹配不到锚杆-锚杆接触）。须用 `range group 'anchor_ball' match 2`（本项目已落地）精确限定“两端都属 anchor_ball”。
  - 锚杆胶结强度 `pb_ten_anchor/pb_coh_anchor/pb_fa_anchor` 为占位值（默认同岩石量级），可按刚性杆需求独立标定。

## 附：本项目（锚杆拉拔）关键参数约定
- 试样：立方体 50×50×50（半边长 25），x∈[-25,25]。
- 粒径：2~3 均匀分布。
- 锚杆圆柱：锚固端 x=-20（岩内），拉拔端 x=30（岩外），半径 2.0，沿 +x。
- 锚杆颗粒：半径 = 0.8×墙半径 = 1.6，沿 x 轴一行（y=z=0），递增=直径，组 `anchor_ball`；第四步内彼此以 linearpbond 胶结成刚性杆体（pb_ten_anchor=1e6、pb_coh_anchor=1e6、pb_fa_anchor=30，占位值，CMAT id 2（`range group 'anchor_ball' match 2`）定义，施胶只 `contact cmat apply range group 'anchor_ball' match 2` + `contact method bond gap range group 'anchor_ball' match 2`，无需打标 group、不再用 contact property 覆盖），锚杆-岩石界面不胶结（由 `cmat default type ball-ball model linear` 承接）。第六步再定义 `cmat add id 3`（`range fish @is_grout` 精确选跨组界面）把锚杆-岩石界面胶结为浆液粘结（pb_ten_grout/pb_coh_grout=3e5、pb_fa_grout=30，弱于岩石，占位值）。原（岩石）颗粒统一分组 `shiyang`，由 CMAT id 1（`range group 'shiyang' match 2`）单独界定；CMAT 用 `cmat add id` 按颗粒组区分：试样 id 1 `range group 'shiyang' match 2` / 锚杆 id 2 `range group 'anchor_ball' match 2`（组内）/ 界面 id 3 `range fish @is_grout`（跨组，FISH 判两端分属两组），接触类型写在 range 内（不把 `type` 关键字与 `range ball group` 混用）；球-墙(ball-facet)用 `cmat default type`（emod=3×）；ball-ball linearpbond 均含极小参考间隙 `rgap=1e-5`（保证相切颗粒可胶结）。
- 接触/胶结参数（kn/ks/pb_* 等）目前为占位值，需标定到目标宏观力学参数。
- 已交付脚本（按 save/restore 链拆分）：`01_sample_build.dat`、`02_add_anchor.dat`、`03_bond.dat`、`04_anchor_balls.dat`、`05_pullout.dat`、`06_grout.dat`、`07_free_balance.dat`。
