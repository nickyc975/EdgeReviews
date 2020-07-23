# Edge Chromium 扩展评价爬虫

### 来由

Edge Chromium扩展商店里每个扩展的评价都是按地区显示的，没办法一次看到所有评价，而且每次切换地区都得重新搜索扩展名然后才能点进去查看，对于想要从这些评价里收集反馈信息的开发者来说实在是太不友好了。

于是我开发了这个小脚本，可以直接爬取给定扩展的所有评价，妈妈再也不用担心我漏看评价啦！

### 用法

* 获取评价用于统计分析

```python
    getter = ReviewsGetter("<扩展的crx id>")
    reviews = getter.get_reviews()
```

* 将评价保存为Markdown表格

```python
    getter = ReviewsGetter("<扩展的crx id>")
    getter.save_reviews("<文件路径>")
```
