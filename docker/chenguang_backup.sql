-- MySQL dump 10.13  Distrib 26.7.0, for Linux (x86_64)
--
-- Host: localhost    Database: chenguang
-- ------------------------------------------------------
-- Server version	26.7.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
SET @MYSQLDUMP_TEMP_LOG_BIN = @@SESSION.SQL_LOG_BIN;
SET @@SESSION.SQL_LOG_BIN= 0;

--
-- GTID state at the beginning of the backup 
--

SET @@GLOBAL.GTID_PURGED=/*!80000 '+'*/ '589e8ae7-b343-11f1-805e-0ea55c03e3b4:1-122';

--
-- Table structure for table `agent_versions`
--

DROP TABLE IF EXISTS `agent_versions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `agent_versions` (
  `agent_id` bigint NOT NULL COMMENT '所属 Agent ID',
  `version` varchar(50) NOT NULL COMMENT '版本号',
  `config` json DEFAULT NULL COMMENT '该版本的配置快照',
  `changelog` varchar(500) DEFAULT NULL COMMENT '变更说明',
  `is_current` tinyint(1) NOT NULL COMMENT '是否为当前版本',
  `published_by` varchar(100) DEFAULT NULL COMMENT '发布者',
  `published_at` datetime DEFAULT NULL COMMENT '发布时间',
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `agent_id` (`agent_id`),
  CONSTRAINT `agent_versions_ibfk_1` FOREIGN KEY (`agent_id`) REFERENCES `agents` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `agent_versions`
--

LOCK TABLES `agent_versions` WRITE;
/*!40000 ALTER TABLE `agent_versions` DISABLE KEYS */;
INSERT INTO `agent_versions` VALUES (1,'v0.2','{\"rag\": {\"enabled\": true, \"knowledgeBaseIds\": [1]}, \"model\": {\"maxTokens\": 2048, \"temperature\": 0.7}, \"tools\": {\"enabled\": true, \"toolIds\": [1]}, \"prompt\": {\"systemPrompt\": \"你是运维专家\"}, \"advanced\": null}','发布生产v1.0',1,NULL,'2026-09-19 11:04:30',1,'2026-09-19 03:04:29','2026-09-19 03:04:29');
/*!40000 ALTER TABLE `agent_versions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `agents`
--

DROP TABLE IF EXISTS `agents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `agents` (
  `name` varchar(200) NOT NULL COMMENT 'Agent 名称',
  `description` text COMMENT '描述',
  `type` varchar(50) NOT NULL COMMENT '类型: conversation/tool/analysis/creative/workflow',
  `status` varchar(50) NOT NULL COMMENT '状态: active/inactive/error/draft',
  `model_id` bigint DEFAULT NULL COMMENT '关联的模型ID',
  `config` json DEFAULT NULL COMMENT 'Agent 完整配置',
  `success_rate` decimal(5,2) NOT NULL COMMENT '成功率 %',
  `call_count_7d` int NOT NULL COMMENT '近7天调用次数',
  `version` varchar(50) NOT NULL COMMENT '当前版本号',
  `created_by` varchar(100) DEFAULT NULL COMMENT '创建者',
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `model_id` (`model_id`),
  CONSTRAINT `agents_ibfk_1` FOREIGN KEY (`model_id`) REFERENCES `models` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `agents`
--

LOCK TABLES `agents` WRITE;
/*!40000 ALTER TABLE `agents` DISABLE KEYS */;
INSERT INTO `agents` VALUES ('智能运维助手_1789787069','负责监控报警处置与知识问答','conversation','inactive',1,'{\"rag\": {\"enabled\": true, \"knowledgeBaseIds\": [1]}, \"model\": {\"maxTokens\": 2048, \"temperature\": 0.7}, \"tools\": {\"enabled\": true, \"toolIds\": [1]}, \"prompt\": {\"systemPrompt\": \"你是运维专家\"}, \"advanced\": null}',0.00,0,'v0.2',NULL,1,'2026-09-19 03:04:29','2026-09-19 03:04:29');
/*!40000 ALTER TABLE `agents` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

LOCK TABLES `alembic_version` WRITE;
/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
INSERT INTO `alembic_version` VALUES ('dd01e8b51ef7');
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `documents`
--

DROP TABLE IF EXISTS `documents`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `documents` (
  `knowledge_base_id` bigint NOT NULL COMMENT '所属知识库ID',
  `file_name` varchar(500) NOT NULL COMMENT '文件名',
  `file_type` varchar(50) NOT NULL COMMENT '文件类型: pdf/docx/md/txt/html/csv',
  `file_size` varchar(50) DEFAULT NULL COMMENT '文件大小',
  `status` varchar(50) NOT NULL COMMENT '处理状态: pending/processing/completed/failed',
  `segment_count` int NOT NULL COMMENT '分段数量',
  `word_count` int NOT NULL COMMENT '字数',
  `error_message` text COMMENT '错误信息',
  `uploaded_by` varchar(100) DEFAULT NULL COMMENT '上传者',
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '更新时间',
  `minio_path` varchar(1000) DEFAULT NULL COMMENT 'MinIO 存储路径',
  `processed_at` datetime DEFAULT NULL COMMENT '处理完成时间',
  PRIMARY KEY (`id`),
  KEY `knowledge_base_id` (`knowledge_base_id`),
  CONSTRAINT `documents_ibfk_1` FOREIGN KEY (`knowledge_base_id`) REFERENCES `knowledge_bases` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `documents`
--

LOCK TABLES `documents` WRITE;
/*!40000 ALTER TABLE `documents` DISABLE KEYS */;
INSERT INTO `documents` VALUES (1,'manual.txt','txt','0.00 MB','pending',0,0,NULL,NULL,1,'2026-09-19 03:04:29','2026-09-19 03:04:29',NULL,NULL),(1,'员工福利体系管理规范.md','md','10.73 KB','pending',0,0,NULL,NULL,5,'2026-09-19 09:03:58','2026-09-19 09:03:58','kb/1/09202fdf76bf454da324fc505f9eaee0_员工福利体系管理规范.md',NULL),(4,'劳动合同.docx','docx','25.74 KB','pending',0,0,NULL,NULL,6,'2026-09-19 09:12:02','2026-09-19 09:12:02','kb/4/a88ccf710c4e4997a1ca0ffb3bd23742_劳动合同.docx',NULL),(4,'员工福利体系管理规范.md','md','10.73 KB','pending',0,0,NULL,NULL,7,'2026-09-19 09:12:02','2026-09-19 09:12:02','kb/4/2e738ff2e57d47caa5b4cd3e9ffb97b3_员工福利体系管理规范.md',NULL);
/*!40000 ALTER TABLE `documents` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `knowledge_bases`
--

DROP TABLE IF EXISTS `knowledge_bases`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `knowledge_bases` (
  `name` varchar(200) NOT NULL COMMENT '知识库名称',
  `description` varchar(500) DEFAULT NULL COMMENT '描述',
  `status` varchar(50) NOT NULL COMMENT '状态: ready/indexing/error/empty',
  `document_count` int NOT NULL COMMENT '文档数量',
  `segment_count` int NOT NULL COMMENT '分段数量',
  `embedding_model` varchar(100) NOT NULL COMMENT '向量化模型',
  `created_by` varchar(100) DEFAULT NULL COMMENT '创建者',
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '更新时间',
  `chunk_method` varchar(20) NOT NULL COMMENT '分段方式: fixed/sentence/paragraph',
  `chunk_size` int NOT NULL COMMENT '分段大小（tokens）',
  `chunk_overlap` int NOT NULL COMMENT '重叠大小（tokens）',
  `retrieval_strategy` varchar(20) NOT NULL COMMENT '检索策略: vector/fulltext/hybrid',
  `top_k` int NOT NULL COMMENT '返回结果数',
  `similarity_threshold` float NOT NULL COMMENT '相似度阈值',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `knowledge_bases`
--

LOCK TABLES `knowledge_bases` WRITE;
/*!40000 ALTER TABLE `knowledge_bases` DISABLE KEYS */;
INSERT INTO `knowledge_bases` VALUES ('企业产品知识库_1789787069','产品手册与技术规范','empty',2,0,'text-embedding-3-small',NULL,1,'2026-09-19 03:04:29','2026-09-19 09:03:58','',0,0,'',0,0),('企业新人入职知识库','','empty',2,0,'text-embedding-3-small',NULL,4,'2026-09-19 09:11:58','2026-09-19 09:12:02','fixed',500,50,'hybrid',5,0.7);
/*!40000 ALTER TABLE `knowledge_bases` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `model_providers`
--

DROP TABLE IF EXISTS `model_providers`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `model_providers` (
  `name` varchar(100) NOT NULL COMMENT '供应商名称',
  `type` varchar(50) NOT NULL COMMENT '供应商类型: openai/anthropic/aliyun/azure/local/custom',
  `status` varchar(50) NOT NULL COMMENT '连接状态: connected/disconnected/error',
  `endpoint` varchar(500) NOT NULL COMMENT 'API端点地址',
  `api_key` text COMMENT 'API密钥（加密存储）',
  `description` varchar(500) DEFAULT NULL COMMENT '供应商描述',
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '更新时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `model_providers`
--

LOCK TABLES `model_providers` WRITE;
/*!40000 ALTER TABLE `model_providers` DISABLE KEYS */;
INSERT INTO `model_providers` VALUES ('OpenAI 官方','openai','connected','https://api.openai.com/v1','sk-test-123456','更新后的描述',1,'2026-09-19 03:03:39','2026-09-19 03:03:39'),('OpenAI 官方_1789787069','openai','connected','https://api.openai.com/v1','sk-test-123456','更新后的描述',2,'2026-09-19 03:04:29','2026-09-19 03:04:29'),('阿里云百炼Dashscope','aliyun','connected','https://dashscope.aliyuncs.com/compatible-mode/v1','sk-7bee6d2542474b79931b53542b3f9cd3','',6,'2026-09-19 09:07:18','2026-09-20 08:02:32');
/*!40000 ALTER TABLE `model_providers` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `models`
--

DROP TABLE IF EXISTS `models`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `models` (
  `name` varchar(100) NOT NULL COMMENT '模型显示名称',
  `model_id` varchar(100) NOT NULL COMMENT '模型标识符，如 gpt-4',
  `provider_id` bigint NOT NULL COMMENT '所属供应商ID',
  `capabilities` varchar(500) DEFAULT NULL COMMENT '能力标签，逗号分隔: function_call,vision,streaming',
  `context_length` int NOT NULL COMMENT '上下文窗口大小',
  `status` varchar(50) NOT NULL COMMENT '状态: available/unavailable/rate_limited',
  `input_price` decimal(10,6) NOT NULL COMMENT '输入价格（每1K tokens）',
  `output_price` decimal(10,6) NOT NULL COMMENT '输出价格（每1K tokens）',
  `currency` varchar(10) NOT NULL COMMENT '货币单位',
  `is_default` tinyint(1) NOT NULL COMMENT '是否为默认模型',
  `description` text COMMENT '模型描述',
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `model_id` (`model_id`),
  KEY `provider_id` (`provider_id`),
  CONSTRAINT `models_ibfk_1` FOREIGN KEY (`provider_id`) REFERENCES `model_providers` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=54 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `models`
--

LOCK TABLES `models` WRITE;
/*!40000 ALTER TABLE `models` DISABLE KEYS */;
INSERT INTO `models` VALUES ('GPT-4o_1789787069','gpt-4o_1789787069',2,'chat,vision,function_calling',131072,'available',0.005000,0.015000,'USD',1,'旗舰全模态模型',1,'2026-09-19 03:04:29','2026-09-19 03:04:29'),('Qwen3.8-Flash','qwen3.8-flash',6,'image,chat',1000000,'available',0.800000,2.700000,'M tokens',0,'Qwen3.8-Flash 是千问最新推出的多模态大模型，兼具强大的理解与生成能力和出色的响应速度。模型原生支持百万级上下文窗口，能够一次性处理超长文档、代码仓库和复杂对话。在编程辅助、智能体协作、图文理解等场景中表现尤为出色——无论是自动修复代码、操作桌面应用，还是分析图表与长视频，都能给出准确、高质量的结果。同时兼容 OpenAI 与 Anthropic 主流接口协议，可无缝接入 Claude Code、Codex 等开发者工具，轻松构建高并发应用与智能工作流。凭借优异的性能与极具竞争力的推理成本，Qwen3.8-Flash 是开发者和企业在 AI 应用中兼顾效果与效率的理想选择。',3,'2026-09-20 08:05:15','2026-09-20 08:05:15');
/*!40000 ALTER TABLE `models` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `permissions`
--

DROP TABLE IF EXISTS `permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `permissions` (
  `code` varchar(100) NOT NULL COMMENT '权限编码',
  `name` varchar(100) NOT NULL COMMENT '权限名称',
  `description` varchar(200) DEFAULT NULL COMMENT '权限描述',
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `permissions`
--

LOCK TABLES `permissions` WRITE;
/*!40000 ALTER TABLE `permissions` DISABLE KEYS */;
INSERT INTO `permissions` VALUES ('user:read','查看用户','查看用户列表及详情',1,'2026-09-18 14:50:08','2026-09-18 14:50:08'),('user:create','创建用户','新增系统用户账号',2,'2026-09-18 14:50:08','2026-09-18 14:50:08'),('user:update','编辑用户','修改用户信息及角色分配',3,'2026-09-18 14:50:08','2026-09-18 14:50:08'),('user:delete','删除用户','删除或停用系统用户',4,'2026-09-18 14:50:08','2026-09-18 14:50:08'),('role:read','查看角色','查看角色列表及权限',5,'2026-09-18 14:50:08','2026-09-18 14:50:08'),('role:create','创建角色','新增系统角色',6,'2026-09-18 14:50:08','2026-09-18 14:50:08'),('role:update','编辑角色','修改角色信息及权限配置',7,'2026-09-18 14:50:08','2026-09-18 14:50:08'),('role:delete','删除角色','删除系统角色',8,'2026-09-18 14:50:08','2026-09-18 14:50:08'),('permission:read','查看权限','查看权限列表',9,'2026-09-18 14:50:08','2026-09-18 14:50:08'),('permission:create','创建权限','定义新权限',10,'2026-09-18 14:50:08','2026-09-18 14:50:08'),('permission:update','编辑权限','修改权限定义',11,'2026-09-18 14:50:08','2026-09-18 14:50:08'),('permission:delete','删除权限','删除权限定义',12,'2026-09-18 14:50:08','2026-09-18 14:50:08'),('agent:read','查看Agent','查看智能体列表及详情',13,'2026-09-18 14:50:08','2026-09-18 14:50:08'),('agent:create','创建Agent','新建智能体',14,'2026-09-18 14:50:08','2026-09-18 14:50:08'),('agent:update','编辑Agent','配置与调试智能体',15,'2026-09-18 14:50:08','2026-09-18 14:50:08'),('agent:delete','删除Agent','删除智能体',16,'2026-09-18 14:50:08','2026-09-18 14:50:08'),('model:read','查看模型','查看大语言模型列表',17,'2026-09-18 14:50:08','2026-09-18 14:50:08'),('model:create','接入模型','添加新模型配置',18,'2026-09-18 14:50:09','2026-09-18 14:50:09'),('knowledge:read','查看知识库','查看RAG知识库列表',19,'2026-09-18 14:50:09','2026-09-18 14:50:09'),('knowledge:create','创建知识库','新建RAG知识库并上传文档',20,'2026-09-18 14:50:09','2026-09-18 14:50:09'),('tool:read','查看工具','查看可用工具列表',21,'2026-09-18 14:50:09','2026-09-18 14:50:09'),('tool:create','注册工具','注册外部API工具',22,'2026-09-18 14:50:09','2026-09-18 14:50:09');
/*!40000 ALTER TABLE `permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prompt_versions`
--

DROP TABLE IF EXISTS `prompt_versions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `prompt_versions` (
  `prompt_id` bigint NOT NULL COMMENT '所属 Prompt ID',
  `version` varchar(50) NOT NULL COMMENT '版本号',
  `content` text NOT NULL COMMENT '该版本的内容快照',
  `changelog` varchar(500) DEFAULT NULL COMMENT '变更说明',
  `is_current` tinyint(1) NOT NULL COMMENT '是否为当前版本',
  `published_by` varchar(100) DEFAULT NULL COMMENT '发布者',
  `published_at` datetime DEFAULT NULL COMMENT '发布时间',
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `prompt_id` (`prompt_id`),
  CONSTRAINT `prompt_versions_ibfk_1` FOREIGN KEY (`prompt_id`) REFERENCES `prompts` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prompt_versions`
--

LOCK TABLES `prompt_versions` WRITE;
/*!40000 ALTER TABLE `prompt_versions` DISABLE KEYS */;
INSERT INTO `prompt_versions` VALUES (1,'v0.2','你是辰光智能助手，请礼貌回答用户问题。','发布正式v1.0版本',0,NULL,'2026-09-19 11:04:30',1,'2026-09-19 03:04:29','2026-09-19 09:11:17'),(1,'v0.3','你是辰光智能助手，请礼貌回答用户问题。','优化回复语气',1,NULL,'2026-09-19 12:28:50',4,'2026-09-19 04:28:49','2026-09-19 09:11:17');
/*!40000 ALTER TABLE `prompt_versions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prompts`
--

DROP TABLE IF EXISTS `prompts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `prompts` (
  `name` varchar(200) NOT NULL COMMENT 'Prompt 名称',
  `description` varchar(500) DEFAULT NULL COMMENT '描述',
  `category` varchar(50) NOT NULL COMMENT '分类',
  `tags` json DEFAULT NULL COMMENT '标签列表，JSON 数组',
  `content` text NOT NULL COMMENT 'Prompt 正文内容',
  `variables` json DEFAULT NULL COMMENT '变量定义，JSON 数组',
  `version` varchar(50) NOT NULL COMMENT '当前版本号',
  `status` varchar(50) NOT NULL COMMENT '状态: draft/published',
  `created_by` varchar(100) DEFAULT NULL COMMENT '创建者',
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '更新时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prompts`
--

LOCK TABLES `prompts` WRITE;
/*!40000 ALTER TABLE `prompts` DISABLE KEYS */;
INSERT INTO `prompts` VALUES ('智能客服提示词','用于售前售后客服','customer-service','[\"客服\", \"官方\"]','你是辰光智能助手，请礼貌回答用户问题。','[{\"name\": \"user_name\", \"type\": \"string\", \"required\": false, \"description\": \"用户姓名\", \"default_value\": null}]','v0.3','published',NULL,1,'2026-09-19 03:04:29','2026-09-19 09:11:17');
/*!40000 ALTER TABLE `prompts` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `role_permissions`
--

DROP TABLE IF EXISTS `role_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `role_permissions` (
  `role_id` bigint NOT NULL,
  `permission_id` bigint NOT NULL,
  PRIMARY KEY (`role_id`,`permission_id`),
  KEY `permission_id` (`permission_id`),
  CONSTRAINT `role_permissions_ibfk_1` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`id`) ON DELETE CASCADE,
  CONSTRAINT `role_permissions_ibfk_2` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role_permissions`
--

LOCK TABLES `role_permissions` WRITE;
/*!40000 ALTER TABLE `role_permissions` DISABLE KEYS */;
INSERT INTO `role_permissions` VALUES (1,1),(3,1),(4,1),(1,2),(1,3),(1,4),(1,5),(4,5),(1,6),(1,7),(1,8),(1,9),(4,9),(1,10),(1,11),(1,12),(1,13),(2,13),(3,13),(4,13),(1,14),(2,14),(1,15),(2,15),(1,16),(2,16),(1,17),(2,17),(4,17),(1,18),(2,18),(1,19),(2,19),(3,19),(4,19),(1,20),(2,20),(1,21),(2,21),(4,21),(1,22),(2,22);
/*!40000 ALTER TABLE `role_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `roles`
--

DROP TABLE IF EXISTS `roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `roles` (
  `code` varchar(100) NOT NULL COMMENT '角色编码',
  `name` varchar(100) NOT NULL COMMENT '角色名称',
  `description` varchar(200) DEFAULT NULL COMMENT '角色描述',
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `roles`
--

LOCK TABLES `roles` WRITE;
/*!40000 ALTER TABLE `roles` DISABLE KEYS */;
INSERT INTO `roles` VALUES ('admin','超级管理员','拥有系统所有功能与最高管控权限',1,'2026-09-18 14:50:09','2026-09-18 14:50:09'),('developer','开发者','负责模型接入、Agent创建与开发测试',2,'2026-09-18 14:50:09','2026-09-18 14:50:09'),('operator','运营人员','日常对话日志分析、效果监控与基本管理',3,'2026-09-18 14:50:09','2026-09-18 14:50:09'),('viewer','访客','仅具备基本浏览与体验权限',4,'2026-09-18 14:50:09','2026-09-18 14:50:09');
/*!40000 ALTER TABLE `roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `segments`
--

DROP TABLE IF EXISTS `segments`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `segments` (
  `knowledge_base_id` bigint NOT NULL COMMENT '所属知识库ID',
  `document_id` bigint NOT NULL COMMENT '所属文档ID',
  `position` int NOT NULL COMMENT '在文档中的位置序号',
  `content` text NOT NULL COMMENT '分段内容',
  `word_count` int NOT NULL COMMENT '字数',
  `token_count` int NOT NULL COMMENT 'Token 数',
  `hit_count` int NOT NULL COMMENT '检索命中次数',
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `document_id` (`document_id`),
  KEY `knowledge_base_id` (`knowledge_base_id`),
  CONSTRAINT `segments_ibfk_1` FOREIGN KEY (`document_id`) REFERENCES `documents` (`id`) ON DELETE CASCADE,
  CONSTRAINT `segments_ibfk_2` FOREIGN KEY (`knowledge_base_id`) REFERENCES `knowledge_bases` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `segments`
--

LOCK TABLES `segments` WRITE;
/*!40000 ALTER TABLE `segments` DISABLE KEYS */;
/*!40000 ALTER TABLE `segments` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tools`
--

DROP TABLE IF EXISTS `tools`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tools` (
  `name` varchar(200) NOT NULL COMMENT '工具名称',
  `description` text COMMENT '工具描述',
  `type` varchar(50) NOT NULL COMMENT '工具类型: builtin/http_api/custom_function',
  `status` varchar(50) NOT NULL COMMENT '状态: enabled/disabled/error',
  `config` json DEFAULT NULL COMMENT '工具配置（因类型而异）',
  `function_definition` json DEFAULT NULL COMMENT 'Function Calling 定义（OpenAI 格式）',
  `call_count_7d` int NOT NULL COMMENT '近7天调用次数',
  `success_rate` decimal(5,2) NOT NULL COMMENT '成功率 %',
  `avg_latency` int NOT NULL COMMENT '平均延迟 ms',
  `created_by` varchar(100) DEFAULT NULL COMMENT '创建者',
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tools`
--

LOCK TABLES `tools` WRITE;
/*!40000 ALTER TABLE `tools` DISABLE KEYS */;
INSERT INTO `tools` VALUES ('weather_lookup_1789787069','根据城市查询实时天气','http_api','disabled','{\"url\": \"https://api.weather.com/v1\", \"method\": \"GET\"}','{\"name\": \"weather_lookup_1789787069\", \"parameters\": {\"type\": \"object\", \"required\": [\"city\"], \"properties\": {\"city\": {\"type\": \"string\", \"description\": \"城市名称\"}}}, \"description\": \"查询城市天气\"}',0,0.00,0,NULL,1,'2026-09-19 03:04:29','2026-09-19 03:04:29'),('网页搜索','查询网页内容','http_api','disabled','{\"url\": \"\", \"method\": \"GET\", \"headers\": {}, \"timeout\": 10000}','{\"name\": \"网页搜索\", \"parameters\": {\"type\": \"object\", \"required\": [], \"properties\": {}}, \"description\": \"查询网页内容\"}',0,0.00,0,NULL,2,'2026-09-19 09:13:33','2026-09-19 09:13:42');
/*!40000 ALTER TABLE `tools` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_roles`
--

DROP TABLE IF EXISTS `user_roles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_roles` (
  `user_id` bigint NOT NULL,
  `role_id` bigint NOT NULL,
  PRIMARY KEY (`user_id`,`role_id`),
  KEY `role_id` (`role_id`),
  CONSTRAINT `user_roles_ibfk_1` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE,
  CONSTRAINT `user_roles_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_roles`
--

LOCK TABLES `user_roles` WRITE;
/*!40000 ALTER TABLE `user_roles` DISABLE KEYS */;
INSERT INTO `user_roles` VALUES (1,1),(3,2);
/*!40000 ALTER TABLE `user_roles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `username` varchar(50) NOT NULL COMMENT '用户名',
  `email` varchar(100) NOT NULL COMMENT '邮箱',
  `hashed_password` varchar(255) NOT NULL COMMENT '密码哈希',
  `is_active` tinyint(1) NOT NULL COMMENT '是否启用',
  `id` bigint NOT NULL AUTO_INCREMENT,
  `created_at` datetime NOT NULL DEFAULT (now()) COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT (now()) COMMENT '更新时间',
  `is_superuser` tinyint(1) NOT NULL COMMENT '是否为超级管理员',
  `last_login` datetime DEFAULT NULL COMMENT '最后登录时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_email` (`email`),
  UNIQUE KEY `ix_users_username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES ('admin','admin@example.com','$2b$12$biA7shiW9S9yTgdaE7huJ.oqhyoA8vdhW6PBSg9RgFEwHXeNJoWPe',1,1,'2026-09-18 14:50:09','2026-09-18 15:22:53',1,'2026-09-18 23:22:54'),('ouyangtao','oyt@qq.com','$2b$12$YDMNNfqe5gQ2wTIT6jb.2.HMdUkUy/1Lp7GKFiHYPvcw6kcf0em0m',1,3,'2026-09-18 15:23:38','2026-09-19 09:15:45',0,'2026-09-19 17:15:45');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
SET @@SESSION.SQL_LOG_BIN = @MYSQLDUMP_TEMP_LOG_BIN;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-22 13:34:28
