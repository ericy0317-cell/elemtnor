# Elementor 建站经验总结 (WordPress Elementor Builder Skill)

## 核心架构

### 技术栈
- WordPress + Elementor (Free 3.19.3 + Pro 3.19.3)
- 本地环境: XAMPP (Apache + MariaDB + PHP 8.2)
- WordPress 路径: `D:\wordpress\site`
- MySQL 路径: `C:\xampp\mysql\bin\mysql.exe`
- 数据库: `wordpress_db` / 用户: `wp_user` / 密码: `wp_password123`

### Elementor Container Mode
- **Elementor 3.19.3 默认 Container Mode 关闭**
- 必须使用 `section > column > widget` 结构 (最大深度2层)
- 不能用 `e_container` 或 container 相关API

---

## 页面构建流程

### 1. 页面准备

```php
// 设置全宽模板 (via REST API)
POST /wp-json/wp/v2/pages/{id} {
  "template": "elementor_header_footer"
}
```

### 2. 数据格式

```json
[{
  "id": "section_id",        // 唯一ID
  "elType": "section",
  "settings": { ... },
  "elements": [{
    "id": "column_id",
    "elType": "column",
    "settings": {
      "_column_size": 100,
      "_inline_size": 100,
      "content_position": "center",
      "align": "center"
    },
    "elements": [{
      "id": "widget_id",
      "elType": "widget",
      "widgetType": "html",
      "settings": { "html": "..." }
    }]
  }]
}]
```

### 3. 关键 Meta 字段

| meta_key | 值 | 说明 |
|---|---|---|
| `_elementor_data` | JSON string | 页面元素数据 |
| `_elementor_edit_mode` | `builder` | 标记为 Elementor 构建 |
| `_elementor_template_type` | `wp-page` | 页面模板类型 |
| `_elementor_version` | `3.19.3` | 版本号 |
| `_wp_page_template` | `elementor_header_footer` | WordPress 全宽模板 |

### 4. 保存数据 (关键)

**❌ 不要直接写 MySQL**
直接 MySQL INSERT 会导致 JSON 缺少转义，`json_decode` 失败。

**✅ 必须用 WordPress API + wp_slash()**
```php
// 通过 wp-load.php 加载 WordPress
require_once("D:\\wordpress\\site\\wp-load.php");

// JSON 数据
$elementor_data = \'[{...}]\';

// 用 wp_slash() 确保转义正确
update_post_meta($post_id, "_elementor_data", wp_slash($elementor_data));

// 同时设置其他 meta
update_post_meta($post_id, "_elementor_template_type", "wp-page");
update_post_meta($post_id, "_elementor_edit_mode", "builder");
update_post_meta($post_id, "_elementor_version", "3.19.3");
```

### 5. Default Kit 管理

如果出现 "Your site doesn't have a default kit" 错误:
```sql
INSERT INTO wp_options (option_name, option_value, autoload) 
VALUES ("elementor_active_kit", "8", "yes") 
ON DUPLICATE KEY UPDATE option_value = "8";
```

Kit 通常 ID=8，需要确保 `wp_posts` 中有对应的 `elementor_library` 记录。

### 6. CSS 生成

Elementor CSS 在页面访问时自动生成。如果样式没应用，清除 CSS 缓存：
```php
update_post_meta($post_id, "_elementor_css", "");
```

---

## Widget 选择策略

### ✅ 推荐: HTML Widget
- **所有内容都用 HTML widget** (widgetType: "html")
- 直接在 HTML 中使用 inline styles
- 可靠、可编辑、可预览
- 支持 hover 效果 (onmouseover/onmouseout)

### ❌ 避免: Heading / Text Editor / Button Widget
- Button widget 在嵌套时不持久化
- Heading widget 样式依赖 CSS 文件生成
- Text editor widget 样式可能不生效

### 为什么用 HTML Widget?
1. 深度2层 (section > column > widget)，Elementor 支持良好
2. inline styles 立即生效，不依赖 CSS 文件生成
3. 编辑器中可编辑内容
4. 支持 JavaScript 交互 (hover, click)

---

## 模块构建模式

### HEAD / Hero 模块 (标准模式)
```
Section (full_width, bg image + overlay)
  └─ Column (100%, center)
      ├─ HTML: Eyebrow (橙色标签)
      ├─ HTML: H1 Title (Oswald, 62px, 白色)
      ├─ HTML: Description (Inter, 18px, rgba(255,255,255,0.82))
      └─ HTML: CTA Buttons (flex, hover效果)
```

### 按钮 hover 效果实现
```html
<a href="#" style="transition:all 0.3s ease;background:#E87C2A;"
   onmouseover="this.style.background=\'#d06d20\'"
   onmouseout="this.style.background=\'#E87C2A\'">
  Button Text
</a>
```

### Why Choose 模块 (4列)
```
Section (bg:#1a1a1a)
  ├─ Column (25%) → HTML icon + HTML heading + HTML text
  ├─ Column (25%) → ...
  ├─ Column (25%) → ...
  └─ Column (25%) → ...
```

---

## 调试技巧

### 检查 JSON 有效性
```php
$check = get_post_meta($post_id, "_elementor_data", true);
$decoded = json_decode($check, true);
if (!is_array($decoded)) {
    echo "JSON error: " . json_last_error_msg();
}
```

### 检查前端渲染
```python
import requests
r = requests.get("http://wordpress.local/page-url/")
text = r.text
# 检查 Elementor 类
print("elementor" in text)  # 应该是 True
print("elementor-section" in text)  # 应该是 True
# 检查内容
print("预期文本" in text)
```

### 检查文档对象
```php
$document = \Elementor\Plugin::$instance->documents->get_doc_for_frontend($post_id);
if ($document) {
    echo "is_built_with_elementor: " . $document->is_built_with_elementor();
    echo "elements: " . count($document->get_elements_data());
}
```

---

## 保存数据的三种方式

### 方式1: PHP + wp_slash() ✅ 推荐
```php
update_post_meta(12, "_elementor_data", wp_slash($json_string));
```

### 方式2: 直接 MySQL (不推荐)
```bash
mysql -u user -p db -e "INSERT INTO wp_postmeta ..."
```
⚠️ 可能丢失转义，JSON 解析失败

### 方式3: Elementor AJAX (需浏览器)
```javascript
elementorCommon.ajax.addRequest("save_builder", {
  data: { post_id: 12, status: "draft" }
});
```

---

## 常见问题

1. **"Your site doesn't have a default kit"** → 设置 `elementor_active_kit` 选项
2. **内容渲染但无样式** → 清除 `_elementor_css` meta
3. **JSON 解析失败** → 用 `wp_slash()` 保存，不要直接写 MySQL
4. **Button widget 不持久化** → 改用 HTML widget
5. **Container Mode 不生效** → Elementor 3.19.3 默认关闭，用 section
6. **页面显示"没内容"** → 检查 `post_content` 是否被清空，检查 `_elementor_edit_mode` 是否等于 builder
