# 项目介绍

本项目在设计之初参考和借鉴了[QingdaoU/OnlineJudge](https://github.com/QingdaoU/OnlineJudge)，在此对前辈们表达深深敬意。

YeeOnlineJudge的后端基于Django，配合PostgreSQL、Redis、Celery和Django REST Framework实现。前端……

## 功能

- OnlineJudge的基本功能
- 代码提交预览
- 函数式题目与判题 *开发中*
- 班级（组）的管理 *开发中*
- 博客功能 *开发中*
- ……

## 后端是如何工作的？

后端主要是使用Django框架作为骨架，使用Redis和Celery完成异步任务，Django REST Framework实现RESTfulAPI。
