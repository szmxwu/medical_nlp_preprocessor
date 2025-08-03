# API 文档

## 核心API

### preprocess_text()

主要的便捷函数，用于快速预处理医学文本。

```python
def preprocess_text(
    text: str, 
    version: str = '报告', 
    modality: str = '通用'
) -> List[Dict[str, str]]:
```

**参数**:
- `text` (str): 待处理的医学文本
- `version` (str): 规则版本，可选值：'报告'、'标题'、'申请单'
- `modality` (str): 设备类型，可选值：'通用'、'CT'、'MR'、'DR'、'病理'、'超声'

**返回值**:
- `List[Dict[str, str]]`: 包含分句结果的列表，每个元素为字典
  - 每个字典包含：
    - `"original"`: 原始句子
    - `"preprocessed"`: 处理后的句子

**示例**:
```python
from medical_nlp_preprocessor import preprocess_text

# 基本使用（自动分句）
results = preprocess_text("C1、2椎体骨折。右第5肋骨骨折。")
for i, result in enumerate(results, 1):
    print(f"句子{i} - 原始: {result['original']}")  
    print(f"句子{i} - 处理后: {result['preprocessed']}")  
# 输出: 
# 句子1 - 原始: C1、2椎体骨折
# 句子1 - 处理后: 颈1椎体、颈2椎体骨折
# 句子2 - 原始: 右第5肋骨骨折
# 句子2 - 处理后: 右第5肋骨骨折

# 标题文本处理
results = preprocess_text("颅脑CTA检查")
for result in results:
    print(f"标题处理: {result['preprocessed']}")

# 指定设备类型
results = preprocess_text("胸部CT显示正常。", version='报告', modality='CT')
for result in results:
    print(f"CT专用处理: {result['preprocessed']}")
```

### create_preprocessor()

创建预处理器实例，适用于需要重复处理多个文本的场景。

```python
def create_preprocessor(
    version: str = '报告', 
    modality: str = '通用', 
    enable_cache: bool = True
) -> Preprocessor:
```

**参数**:
- `version` (str): 规则版本
- `modality` (str): 设备类型  
- `enable_cache` (bool): 是否启用缓存，默认True

**返回值**:
- `Preprocessor`: 预处理器实例

**示例**:
```python
from medical_nlp_preprocessor import create_preprocessor

# 创建预处理器
preprocessor = create_preprocessor(
    version='报告',
    modality='CT',
    enable_cache=True
)

# 处理多个文本
texts = ["C1、2椎体骨折。", "L1-3椎体信号异常。", "右第5、6肋骨骨折。"]
for text in texts:
    results = preprocessor.process(text)
    print(f"输入: {text}")
    for result in results:
        print(f"  原始: {result['original']}")
        print(f"  处理后: {result['preprocessed']}")
    print("-" * 30)
```

## 核心类

### Preprocessor

主预处理器类，整合所有预处理功能。

#### 构造函数

```python
def __init__(
    self, 
    version: str = '报告', 
    modality: str = '通用', 
    enable_cache: bool = True
):
```

#### 主要方法

##### process()

处理医学文本的主方法。

```python
def process(self, text: str) -> List[Dict[str, str]]:
```

**参数**:
- `text` (str): 待处理文本

**返回值**:
- `List[Dict[str, str]]`: 包含分句结果的列表，每个元素为字典
  - 每个字典包含：
    - `"original"`: 原始句子
    - `"preprocessed"`: 处理后的句子

##### get_info()

获取预处理器信息。

```python
def get_info(self) -> Dict[str, Any]:
```

**返回值**:
- `dict`: 包含版本、规则数量等信息的字典

##### reload_config()

重新加载配置和规则。

```python
def reload_config(self) -> None:
```

**示例**:
```python
preprocessor = create_preprocessor()

# 处理文本
results = preprocessor.process("第一句医学文本。第二句医学文本。")
for result in results:
    print(f"原始: {result['original']}")
    print(f"处理后: {result['preprocessed']}")

# 获取信息
info = preprocessor.get_info()
print(f"规则数量: {info['text_replacer_info']['total_rules']}")

# 重新加载配置
preprocessor.reload_config()
```

### TextReplacer

文本替换引擎，负责应用替换规则。

#### 构造函数

```python
def __init__(self, version: str = '报告', modality: str = '通用'):
```

#### 主要方法

##### apply_replacements()

应用所有替换规则。

```python
def apply_replacements(self, text: str) -> str:
```

##### get_rule_info()

获取规则信息。

```python
def get_rule_info(self) -> Dict:
```

**示例**:
```python
from medical_nlp_preprocessor.core import TextReplacer

replacer = TextReplacer(version='报告', modality='CT')
result = replacer.apply_replacements("颅脑CTA")
info = replacer.get_rule_info()
```

### MedicalExpander

医学术语扩展器，处理专业缩写。

#### 主要方法

##### expand_all()

应用所有医学扩展。

```python
def expand_all(self, text: str) -> str:
```

##### expand_spine_dot()

扩展椎体顿号形式。

```python
def expand_spine_dot(self, text: str) -> str:
```

##### expand_spine_range()

扩展椎体范围形式。

```python
def expand_spine_range(self, text: str) -> str:
```

##### expand_disk_range()

扩展椎间盘范围形式。

```python
def expand_disk_range(self, text: str) -> str:
```

##### expand_rib_abbreviations()

扩展肋骨缩写形式。

```python
def expand_rib_abbreviations(self, text: str) -> str:
```

**示例**:
```python
from medical_nlp_preprocessor.extensions import MedicalExpander

expander = MedicalExpander()

# 应用所有扩展
result = expander.expand_all("C1、2椎体，右第5、6肋骨")

# 单独应用椎体扩展
result = expander.expand_spine_dot("C1、2椎体")
```

## 配置管理API

### get_config_manager()

获取全局配置管理器实例。

```python
def get_config_manager() -> ConfigManager:
```

### get_config()

获取配置值。

```python
def get_config(section: str, option: str, fallback: Any = None) -> str:
```

### get_config_list()

获取配置列表。

```python
def get_config_list(
    section: str, 
    option: str, 
    separator: str = '|', 
    fallback: list = None
) -> list:
```

**示例**:
```python
from medical_nlp_preprocessor.config import get_config, get_config_list

# 获取单个配置
pattern = get_config('sentence', 'sentence_pattern')

# 获取配置列表
illness_list = get_config_list('positive', 'absolute_illness')
```

## 数据管理API

### load_replacement_rules()

加载替换规则。

```python
def load_replacement_rules(
    version: str, 
    modality: str = '通用', 
    include_general: bool = True
) -> List[ReplacementRule]:
```

**参数**:
- `version` (str): 规则版本
- `modality` (str): 设备类型
- `include_general` (bool): 是否包含通用规则

**返回值**:
- `List[ReplacementRule]`: 规则列表

**示例**:
```python
from medical_nlp_preprocessor.data import load_replacement_rules

# 加载CT设备的报告规则
rules = load_replacement_rules('报告', 'CT', include_general=True)
print(f"加载了 {len(rules)} 条规则")
```

### ReplacementRule

替换规则数据类。

**属性**:
- `original` (str): 原始值
- `replacement` (str): 替换值
- `is_regex` (bool): 是否为正则表达式
- `version` (str): 版本
- `modality` (str): 设备类型

## 工具函数API

### 文本处理工具

```python
from medical_nlp_preprocessor.utils import (
    clean_whitespace,
    normalize_punctuation,
    split_sentences,
    is_valid_medical_text,
    extract_measurements
)

# 清理空白字符
clean_text = clean_whitespace(text)

# 标准化标点符号
normalized = normalize_punctuation(text)

# 分句
sentences = split_sentences(text)

# 验证医学文本
if is_valid_medical_text(text):
    # 处理文本
    pass

# 提取测量值
measurements = extract_measurements(text)
```

### 性能装饰器

```python
from medical_nlp_preprocessor.utils import timing_decorator

@timing_decorator
def my_function():
    # 函数会自动记录执行时间
    pass
```

## 异常处理

### 常见异常

1. **FileNotFoundError**: 配置文件或规则文件不存在
2. **KeyError**: 正则表达式模式不存在
3. **ValueError**: 无效的参数值
4. **RuntimeError**: 运行时错误

### 异常处理示例

```python
from medical_nlp_preprocessor import preprocess_text

try:
    result = preprocess_text(input_text)
except FileNotFoundError as e:
    print(f"文件不存在: {e}")
except ValueError as e:
    print(f"参数错误: {e}")
except Exception as e:
    print(f"处理失败: {e}")
```

## 高级用法

### 自定义扩展器

```python
from medical_nlp_preprocessor.extensions import MedicalExpander

class CustomExpander(MedicalExpander):
    def custom_rule(self, text):
        # 自定义处理逻辑
        return text.replace("特殊词", "标准词")
    
    def expand_all(self, text):
        # 先执行父类的扩展
        text = super().expand_all(text)
        # 再执行自定义扩展
        text = self.custom_rule(text)
        return text

# 使用自定义扩展器
expander = CustomExpander()
result = expander.expand_all("包含特殊词的文本")
```

### 批量处理优化

```python
from medical_nlp_preprocessor import create_preprocessor

def batch_process(texts, batch_size=100):
    """批量处理文本"""
    preprocessor = create_preprocessor(enable_cache=True)
    results = []
    
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i+batch_size]
        batch_results = [preprocessor.process(text) for text in batch]
        results.extend(batch_results)
    
    return results
```

### 性能监控

```python
preprocessor = create_preprocessor(enable_cache=True)

# 处理一些文本
for text in texts:
    result = preprocessor.process(text)

# 获取性能统计
stats = preprocessor.get_processing_stats()
print(f"缓存命中率: {stats['cache_info'].hit_rate}")
```

## 版本兼容性

| 功能 | v1.0.0 |
|------|--------|
| 基础预处理 | ✅ |
| 医学扩展 | ✅ |
| 多设备类型 | ✅ |
| 缓存优化 | ✅ |
| 配置管理 | ✅ |
| 性能监控 | ✅ |

## 最佳实践

1. **重用预处理器实例**: 避免重复创建，提高性能
2. **启用缓存**: 对于重复文本处理场景
3. **选择合适的版本和设备类型**: 获得最佳处理效果
4. **批量处理**: 处理大量文本时使用批量方法
5. **异常处理**: 添加适当的错误处理逻辑

## 调试和诊断

### 获取详细信息

```python
# 获取预处理器详细信息
info = preprocessor.get_info()
print("预处理器信息:", info)

# 获取规则统计
from medical_nlp_preprocessor.data import get_rule_loader
loader = get_rule_loader()
stats = loader.get_rule_statistics()
print("规则统计:", stats)

# 获取可用配置
from medical_nlp_preprocessor.config import get_config_manager
config_manager = get_config_manager()
config_data = config_manager.get_all_config_data()
print("配置数据:", config_data)
```

### 日志配置

```python
import logging

# 配置日志以获取详细信息
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('medical_nlp_preprocessor')
```

这个API文档涵盖了重构后预处理器的所有主要功能和使用方法。如需更多详细信息，请参考源代码中的文档字符串。
