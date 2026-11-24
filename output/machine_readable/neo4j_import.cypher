// ============================================================
// 《平凡的世界》知识图谱 —— Neo4j 导入脚本
// 由 LLM 抽取结果自动生成（entities.json + triples.json）
// 用法: cypher-shell -u neo4j -p <password> -f neo4j_import.cypher
// ============================================================

// 1. 唯一性约束（幂等）
CREATE CONSTRAINT PERSON_name IF NOT EXISTS FOR (n:PERSON) REQUIRE n.name IS UNIQUE;
CREATE CONSTRAINT LOCATION_name IF NOT EXISTS FOR (n:LOCATION) REQUIRE n.name IS UNIQUE;
CREATE CONSTRAINT ORGANIZATION_name IF NOT EXISTS FOR (n:ORGANIZATION) REQUIRE n.name IS UNIQUE;
CREATE CONSTRAINT TIME_name IF NOT EXISTS FOR (n:TIME) REQUIRE n.name IS UNIQUE;
CREATE CONSTRAINT EVENT_name IF NOT EXISTS FOR (n:EVENT) REQUIRE n.name IS UNIQUE;
CREATE CONSTRAINT CONCEPT_name IF NOT EXISTS FOR (n:CONCEPT) REQUIRE n.name IS UNIQUE;

// 2. 创建节点（MERGE 幂等，可重复执行）
MERGE (n:PERSON {name: "孙少平"}) ON CREATE SET n.id = "E01", n.aliases = ["少平"], n.description = "主人公，农民子弟，高中学生→教师→建筑工人→煤矿工人", n.frequency = 12;
MERGE (n:PERSON {name: "孙少安"}) ON CREATE SET n.id = "E02", n.aliases = ["少安"], n.description = "孙少平之兄，责任制先行者，建窑烧砖成冒尖户", n.frequency = 10;
MERGE (n:PERSON {name: "田润叶"}) ON CREATE SET n.id = "E03", n.aliases = ["润叶"], n.description = "田福堂之女，县城教师，与少安青梅竹马，后嫁李向前", n.frequency = 9;
MERGE (n:PERSON {name: "田晓霞"}) ON CREATE SET n.id = "E04", n.aliases = ["晓霞"], n.description = "田福军之女，省报记者，抗洪采访牺牲", n.frequency = 7;
MERGE (n:PERSON {name: "田福堂"}) ON CREATE SET n.id = "E05", n.aliases = ["村支书", "田支书"], n.description = "村支书，反对责任制与少安润叶婚事，组织抢水炸山", n.frequency = 8;
MERGE (n:PERSON {name: "郝红梅"}) ON CREATE SET n.id = "E06", n.aliases = ["红梅"], n.description = "地主家庭出身，与少平有情愫，后嫁顾养民、再嫁田润生", n.frequency = 5;
MERGE (n:PERSON {name: "贺秀莲"}) ON CREATE SET n.id = "E07", n.aliases = ["秀莲"], n.description = "勤劳善良的山西姑娘，孙少安之妻，确诊肺癌", n.frequency = 4;
MERGE (n:PERSON {name: "田润生"}) ON CREATE SET n.id = "E08", n.aliases = ["润生"], n.description = "田福堂之子、润叶之弟，与郝红梅结为夫妻", n.frequency = 5;
MERGE (n:PERSON {name: "李向前"}) ON CREATE SET n.id = "E09", n.aliases = ["向前"], n.description = "钟情润叶，酒后开车致残", n.frequency = 3;
MERGE (n:PERSON {name: "田福军"}) ON CREATE SET n.id = "E10", n.aliases = ["田副主任"], n.description = "县革委副主任，田晓霞之父", n.frequency = 3;
MERGE (n:PERSON {name: "顾养民"}) ON CREATE SET n.id = "E11", n.aliases = ["养民"], n.description = "家境优越，与郝红梅恋爱", n.frequency = 2;
MERGE (n:PERSON {name: "侯玉英"}) ON CREATE SET n.id = "E12", n.aliases = ["玉英"], n.description = "孙少平同班同学，当众说破少平与红梅关系", n.frequency = 1;
MERGE (n:PERSON {name: "金波"}) ON CREATE SET n.id = "E13", n.aliases = [], n.description = "孙少平少时玩伴", n.frequency = 1;
MERGE (n:PERSON {name: "金波之妹"}) ON CREATE SET n.id = "E14", n.aliases = ["金波妹妹"], n.description = "向少平表白被婉拒，原文未具名", n.frequency = 1;
MERGE (n:PERSON {name: "县长"}) ON CREATE SET n.id = "E15", n.aliases = [], n.description = "帮助少安砖窑再度奋起（泛称）", n.frequency = 1;
MERGE (n:LOCATION {name: "原西县"}) ON CREATE SET n.id = "E16", n.aliases = ["原西"], n.description = "故事发生地", n.frequency = 2;
MERGE (n:ORGANIZATION {name: "原西县高中"}) ON CREATE SET n.id = "E17", n.aliases = ["高中", "县高中"], n.description = "孙少平就读学校", n.frequency = 1;
MERGE (n:LOCATION {name: "山西"}) ON CREATE SET n.id = "E18", n.aliases = [], n.description = "少安相亲娶秀莲之地", n.frequency = 1;
MERGE (n:LOCATION {name: "县城"}) ON CREATE SET n.id = "E19", n.aliases = [], n.description = "田润叶任教之地", n.frequency = 1;
MERGE (n:LOCATION {name: "上游"}) ON CREATE SET n.id = "E20", n.aliases = [], n.description = "抢水冲突对象", n.frequency = 1;
MERGE (n:LOCATION {name: "河坝"}) ON CREATE SET n.id = "E21", n.aliases = [], n.description = "田福堂组织偷挖之处", n.frequency = 1;
MERGE (n:LOCATION {name: "煤矿"}) ON CREATE SET n.id = "E22", n.aliases = ["矿山"], n.description = "孙少平后期工作地", n.frequency = 4;
MERGE (n:LOCATION {name: "异乡"}) ON CREATE SET n.id = "E23", n.aliases = [], n.description = "润生与红梅邂逅之地", n.frequency = 1;
MERGE (n:ORGANIZATION {name: "县革委"}) ON CREATE SET n.id = "E24", n.aliases = ["县革命委员会"], n.description = "田福军任职机构", n.frequency = 1;
MERGE (n:ORGANIZATION {name: "生产队"}) ON CREATE SET n.id = "E25", n.aliases = [], n.description = "少安领导实行责任制的基层组织", n.frequency = 2;
MERGE (n:ORGANIZATION {name: "公社"}) ON CREATE SET n.id = "E26", n.aliases = [], n.description = "少安成为冒尖户所在行政单位", n.frequency = 1;
MERGE (n:ORGANIZATION {name: "支部"}) ON CREATE SET n.id = "E27", n.aliases = ["支部会"], n.description = "田福堂召开会议抵制责任制之处", n.frequency = 1;
MERGE (n:ORGANIZATION {name: "省报"}) ON CREATE SET n.id = "E28", n.aliases = [], n.description = "田晓霞任记者单位", n.frequency = 1;
MERGE (n:ORGANIZATION {name: "团地委"}) ON CREATE SET n.id = "E29", n.aliases = [], n.description = "田润叶远离丈夫后工作单位", n.frequency = 1;
MERGE (n:ORGANIZATION {name: "小学"}) ON CREATE SET n.id = "E30", n.aliases = ["扩建的小学"], n.description = "少安出资一万五千元扩建的学校", n.frequency = 2;
MERGE (n:TIME {name: "1975年初"}) ON CREATE SET n.id = "E31", n.aliases = [], n.description = "第一部故事起点", n.frequency = 1;
MERGE (n:TIME {name: "1979年春"}) ON CREATE SET n.id = "E32", n.aliases = [], n.description = "第二部故事起点", n.frequency = 1;
MERGE (n:TIME {name: "1982年"}) ON CREATE SET n.id = "E33", n.aliases = [], n.description = "第三部故事起点", n.frequency = 1;
MERGE (n:TIME {name: "27岁"}) ON CREATE SET n.id = "E34", n.aliases = [], n.description = "少平事故时年龄", n.frequency = 1;
MERGE (n:TIME {name: "两年后"}) ON CREATE SET n.id = "E35", n.aliases = [], n.description = "少平与晓霞相约再会时间", n.frequency = 1;
MERGE (n:EVENT {name: "责任制改革"}) ON CREATE SET n.id = "E36", n.aliases = [], n.description = "少安领导生产队率先实行并全村推广", n.frequency = 2;
MERGE (n:EVENT {name: "偷挖河坝与上游抢水"}) ON CREATE SET n.id = "E37", n.aliases = [], n.description = "田福堂为树威信组织，酿成人命", n.frequency = 1;
MERGE (n:EVENT {name: "炸山修田"}) ON CREATE SET n.id = "E38", n.aliases = [], n.description = "农业学大寨口号下的好大喜功之举", n.frequency = 1;
MERGE (n:EVENT {name: "建窑烧砖"}) ON CREATE SET n.id = "E39", n.aliases = [], n.description = "少安贷款建窑，成为冒尖户", n.frequency = 1;
MERGE (n:EVENT {name: "扩建机器制砖"}) ON CREATE SET n.id = "E40", n.aliases = [], n.description = "技师不懂技术致损失，后在朋友县长帮助下奋起", n.frequency = 1;
MERGE (n:EVENT {name: "抗洪采访"}) ON CREATE SET n.id = "E41", n.aliases = [], n.description = "田晓霞为抢救灾民牺牲", n.frequency = 1;
MERGE (n:EVENT {name: "煤矿事故"}) ON CREATE SET n.id = "E42", n.aliases = [], n.description = "少平为救护徒弟重伤毁容", n.frequency = 1;
MERGE (n:EVENT {name: "出资扩建小学"}) ON CREATE SET n.id = "E43", n.aliases = [], n.description = "秀莲在庆祝会上吐血确诊肺癌", n.frequency = 1;
MERGE (n:CONCEPT {name: "责任制"}) ON CREATE SET n.id = "E44", n.aliases = ["生产责任制"], n.description = "十一届三中全会后农村改革制度", n.frequency = 3;
MERGE (n:CONCEPT {name: "农业学大寨"}) ON CREATE SET n.id = "E45", n.aliases = [], n.description = "时代口号，炸山修田的由头", n.frequency = 1;
MERGE (n:CONCEPT {name: "十一届三中全会"}) ON CREATE SET n.id = "E46", n.aliases = ["三中全会"], n.description = "1978年历史会议，改革起点", n.frequency = 1;
MERGE (n:CONCEPT {name: "冒尖户"}) ON CREATE SET n.id = "E47", n.aliases = [], n.description = "公社对少安致富的称谓", n.frequency = 1;
MERGE (n:CONCEPT {name: "旱灾"}) ON CREATE SET n.id = "E48", n.aliases = [], n.description = "第一部中的自然灾害", n.frequency = 1;
MERGE (n:CONCEPT {name: "肺癌"}) ON CREATE SET n.id = "E49", n.aliases = [], n.description = "抽取过程中新增的实体（LLM 发现）", n.frequency = 1;

// 3. 创建关系（MERGE 幂等，附带原文证据）
MATCH (a {name: "孙少平"}), (b {name: "原西县高中"}) MERGE (a)-[r:STUDY_AT {id: "T01"}]->(b) ON CREATE SET r.evidence = "到原西县高中读书", r.section = "第一部";
MATCH (a {name: "孙少平"}), (b {name: "郝红梅"}) MERGE (a)-[r:CLASSMATE {id: "T02"}]->(b) ON CREATE SET r.evidence = "处境相同的地主家庭出身的郝红梅", r.section = "第一部";
MATCH (a {name: "孙少平"}), (b {name: "侯玉英"}) MERGE (a)-[r:CLASSMATE {id: "T03"}]->(b) ON CREATE SET r.evidence = "被同班同学侯玉英发现", r.section = "第一部";
MATCH (a {name: "孙少平"}), (b {name: "郝红梅"}) MERGE (a)-[r:LOVER {id: "T04"}]->(b) ON CREATE SET r.evidence = "对郝红梅产生情愫", r.section = "第一部";
MATCH (a {name: "侯玉英"}), (b {name: "孙少平"}) MERGE (a)-[r:REVEAL {id: "T05"}]->(b) ON CREATE SET r.evidence = "发现并当众说破", r.section = "第一部";
MATCH (a {name: "郝红梅"}), (b {name: "顾养民"}) MERGE (a)-[r:LOVER {id: "T06"}]->(b) ON CREATE SET r.evidence = "郝红梅却与顾养民恋爱", r.section = "第一部";
MATCH (a {name: "孙少平"}), (b {name: "田晓霞"}) MERGE (a)-[r:FRIEND {id: "T07"}]->(b) ON CREATE SET r.evidence = "与田晓霞建立了友情", r.section = "第一部";
MATCH (a {name: "田福军"}), (b {name: "田晓霞"}) MERGE (a)-[r:FATHER_OF {id: "T08"}]->(b) ON CREATE SET r.evidence = "县革委副主任田福军女儿田晓霞", r.section = "第一部";
MATCH (a {name: "田晓霞"}), (b {name: "孙少平"}) MERGE (a)-[r:HELP {id: "T09"}]->(b) ON CREATE SET r.evidence = "在晓霞帮助下关注着外面的世界", r.section = "第一部";
MATCH (a {name: "孙少安"}), (b {name: "孙少平"}) MERGE (a)-[r:SIBLING {id: "T10"}]->(b) ON CREATE SET r.evidence = "少平的哥哥少安", r.section = "第一部";
MATCH (a {name: "孙少安"}), (b {name: "田润叶"}) MERGE (a)-[r:LOVER {id: "T11"}]->(b) ON CREATE SET r.evidence = "与田润叶青梅竹马，互有爱慕之心", r.section = "第一部";
MATCH (a {name: "田福堂"}), (b {name: "田润叶"}) MERGE (a)-[r:FATHER_OF {id: "T12"}]->(b) ON CREATE SET r.evidence = "村支书田福堂的女儿——县城教师田润叶", r.section = "第一部";
MATCH (a {name: "田润叶"}), (b {name: "县城"}) MERGE (a)-[r:WORK_AT {id: "T13"}]->(b) ON CREATE SET r.evidence = "县城教师田润叶", r.section = "第一部";
MATCH (a {name: "田福堂"}), (b {name: "孙少安"}) MERGE (a)-[r:OPPOSE {id: "T14"}]->(b) ON CREATE SET r.evidence = "少安和润叶互有爱慕之心，却遭到田福堂反对", r.section = "第一部";
MATCH (a {name: "田福堂"}), (b {name: "田润叶"}) MERGE (a)-[r:OPPOSE {id: "T15"}]->(b) ON CREATE SET r.evidence = "遭到田福堂反对（与润叶婚事）", r.section = "第一部";
MATCH (a {name: "孙少安"}), (b {name: "贺秀莲"}) MERGE (a)-[r:SPOUSE {id: "T16"}]->(b) ON CREATE SET r.evidence = "到山西与勤劳善良的秀莲相亲并结了婚", r.section = "第一部";
MATCH (a {name: "贺秀莲"}), (b {name: "山西"}) MERGE (a)-[r:FROM {id: "T17"}]->(b) ON CREATE SET r.evidence = "到山西与秀莲相亲", r.section = "第一部";
MATCH (a {name: "田润叶"}), (b {name: "李向前"}) MERGE (a)-[r:SPOUSE {id: "T18"}]->(b) ON CREATE SET r.evidence = "含泪与李向前结婚", r.section = "第一部";
MATCH (a {name: "田福堂"}), (b {name: "李向前"}) MERGE (a)-[r:INTRODUCE {id: "T19"}]->(b) ON CREATE SET r.evidence = "父亲介绍的一直对她有爱慕之情的李向前", r.section = "第一部";
MATCH (a {name: "李向前"}), (b {name: "田润叶"}) MERGE (a)-[r:LOVER {id: "T20"}]->(b) ON CREATE SET r.evidence = "一直对她有爱慕之情的李向前", r.section = "第一部";
MATCH (a {name: "田福堂"}), (b {name: "偷挖河坝与上游抢水"}) MERGE (a)-[r:ORGANIZE {id: "T21"}]->(b) ON CREATE SET r.evidence = "组织偷挖河坝与上游抢水", r.section = "第一部";
MATCH (a {name: "田福堂"}), (b {name: "炸山修田"}) MERGE (a)-[r:ORGANIZE {id: "T22"}]->(b) ON CREATE SET r.evidence = "他好大喜功炸山修田", r.section = "第一部";
MATCH (a {name: "农业学大寨"}), (b {name: "炸山修田"}) MERGE (a)-[r:MOTIVATE {id: "T23"}]->(b) ON CREATE SET r.evidence = "为了'农业学大寨'……炸山修田", r.section = "第一部";
MATCH (a {name: "偷挖河坝与上游抢水"}), (b {name: "河坝"}) MERGE (a)-[r:LOCATED_AT {id: "T24"}]->(b) ON CREATE SET r.evidence = "偷挖河坝与上游抢水", r.section = "第一部";
MATCH (a {name: "田福堂"}), (b {name: "责任制"}) MERGE (a)-[r:OPPOSE {id: "T25"}]->(b) ON CREATE SET r.evidence = "召开支部会抵制责任制", r.section = "第二部概要";
MATCH (a {name: "田福堂"}), (b {name: "支部"}) MERGE (a)-[r:ORGANIZE {id: "T26"}]->(b) ON CREATE SET r.evidence = "连夜召开支部会", r.section = "第二部概要";
MATCH (a {name: "孙少安"}), (b {name: "生产队"}) MERGE (a)-[r:LEAD {id: "T27"}]->(b) ON CREATE SET r.evidence = "领导生产队率先实行", r.section = "第二部概要";
MATCH (a {name: "孙少安"}), (b {name: "责任制改革"}) MERGE (a)-[r:PARTICIPATE_IN {id: "T28"}]->(b) ON CREATE SET r.evidence = "率先实行，接着在全村推广了责任制", r.section = "第二部概要";
MATCH (a {name: "孙少安"}), (b {name: "建窑烧砖"}) MERGE (a)-[r:PARTICIPATE_IN {id: "T29"}]->(b) ON CREATE SET r.evidence = "用赚的钱建窑烧砖", r.section = "第二部概要";
MATCH (a {name: "孙少安"}), (b {name: "冒尖户"}) MERGE (a)-[r:ACHIEVE {id: "T30"}]->(b) ON CREATE SET r.evidence = "成了公社的'冒尖户'", r.section = "第二部概要";
MATCH (a {name: "孙少平"}), (b {name: "煤矿"}) MERGE (a)-[r:WORK_AT {id: "T31"}]->(b) ON CREATE SET r.evidence = "获得了当煤矿工人的好机遇", r.section = "第二部概要";
MATCH (a {name: "田晓霞"}), (b {name: "省报"}) MERGE (a)-[r:WORK_AT {id: "T32"}]->(b) ON CREATE SET r.evidence = "从师专毕业后到省报当了记者", r.section = "第二部概要";
MATCH (a {name: "孙少平"}), (b {name: "田晓霞"}) MERGE (a)-[r:PROMISE {id: "T33"}]->(b) ON CREATE SET r.evidence = "他们相约两年后再相会", r.section = "第二部概要";
MATCH (a {name: "田润叶"}), (b {name: "团地委"}) MERGE (a)-[r:WORK_AT {id: "T34"}]->(b) ON CREATE SET r.evidence = "到团地委工作", r.section = "第二部概要";
MATCH (a {name: "田润叶"}), (b {name: "李向前"}) MERGE (a)-[r:RETURN_TO {id: "T35"}]->(b) ON CREATE SET r.evidence = "润叶感到内疚回到丈夫身边", r.section = "第二部概要";
MATCH (a {name: "田福堂"}), (b {name: "田润生"}) MERGE (a)-[r:FATHER_OF {id: "T36"}]->(b) ON CREATE SET r.evidence = "她的弟弟润生也已长大成人", r.section = "第二部概要";
MATCH (a {name: "田润生"}), (b {name: "田润叶"}) MERGE (a)-[r:SIBLING {id: "T37"}]->(b) ON CREATE SET r.evidence = "她的弟弟润生", r.section = "第二部概要";
MATCH (a {name: "田润生"}), (b {name: "郝红梅"}) MERGE (a)-[r:SPOUSE {id: "T38"}]->(b) ON CREATE SET r.evidence = "终于两人结为夫妻", r.section = "第二部概要";
MATCH (a {name: "田润生"}), (b {name: "郝红梅"}) MERGE (a)-[r:MEET {id: "T39"}]->(b) ON CREATE SET r.evidence = "在异乡与命运坎坷的郝红梅邂逅", r.section = "第二部概要";
MATCH (a {name: "孙少平"}), (b {name: "田晓霞"}) MERGE (a)-[r:LOVER {id: "T40"}]->(b) ON CREATE SET r.evidence = "孙少平与田晓霞产生强烈感情", r.section = "第三部";
MATCH (a {name: "田晓霞"}), (b {name: "抗洪采访"}) MERGE (a)-[r:DIE_IN {id: "T41"}]->(b) ON CREATE SET r.evidence = "因在抗洪采访中为抢救灾民光荣牺牲", r.section = "第三部";
MATCH (a {name: "田福军"}), (b {name: "孙少平"}) MERGE (a)-[r:INFORM {id: "T42"}]->(b) ON CREATE SET r.evidence = "田福军给孙少平发了封电报", r.section = "第三部";
MATCH (a {name: "孙少平"}), (b {name: "田晓霞"}) MERGE (a)-[r:GRIEVE {id: "T43"}]->(b) ON CREATE SET r.evidence = "少平悲痛不已", r.section = "第三部";
MATCH (a {name: "孙少安"}), (b {name: "扩建机器制砖"}) MERGE (a)-[r:PARTICIPATE_IN {id: "T44"}]->(b) ON CREATE SET r.evidence = "决定贷款扩建机器制砖", r.section = "第三部";
MATCH (a {name: "县长"}), (b {name: "孙少安"}) MERGE (a)-[r:HELP {id: "T45"}]->(b) ON CREATE SET r.evidence = "在朋友和县长的帮助下再度奋起", r.section = "第三部";
MATCH (a {name: "贺秀莲"}), (b {name: "肺癌"}) MERGE (a)-[r:DIAGNOSE_WITH {id: "T46"}]->(b) ON CREATE SET r.evidence = "口吐鲜血，确诊肺癌", r.section = "第三部";
MATCH (a {name: "孙少安"}), (b {name: "小学"}) MERGE (a)-[r:FUNDS {id: "T47"}]->(b) ON CREATE SET r.evidence = "由他家出资一万五千元扩建的小学", r.section = "第三部";
MATCH (a {name: "贺秀莲"}), (b {name: "出资扩建小学"}) MERGE (a)-[r:ATTEND {id: "T48"}]->(b) ON CREATE SET r.evidence = "在欢庆……小学上口吐鲜血", r.section = "第三部";
MATCH (a {name: "田福堂"}), (b {name: "郝红梅"}) MERGE (a)-[r:RECOGNIZE {id: "T49"}]->(b) ON CREATE SET r.evidence = "润生和郝红梅的婚事终于得到了父母的承认", r.section = "第三部";
MATCH (a {name: "孙少平"}), (b {name: "煤矿事故"}) MERGE (a)-[r:INJURED_IN {id: "T50"}]->(b) ON CREATE SET r.evidence = "在一次事故中为救护徒弟也受了重伤", r.section = "第三部";
MATCH (a {name: "金波之妹"}), (b {name: "孙少平"}) MERGE (a)-[r:PROPOSE {id: "T51"}]->(b) ON CREATE SET r.evidence = "遇少时玩伴金波之妹表白", r.section = "第三部";
MATCH (a {name: "孙少平"}), (b {name: "金波之妹"}) MERGE (a)-[r:REJECT {id: "T52"}]->(b) ON CREATE SET r.evidence = "为她的前途与自己的感情选择拒绝", r.section = "第三部";
MATCH (a {name: "孙少平"}), (b {name: "煤矿"}) MERGE (a)-[r:RETURN_TO {id: "T53"}]->(b) ON CREATE SET r.evidence = "又充满信心地回到了矿山", r.section = "第三部";

// 4. 常用查询示例（取消注释即可运行）
// MATCH (p:PERSON)-[r:SPOUSE]->(q) RETURN p.name, q.name;
// MATCH (p:PERSON)-[r:FATHER_OF]->(c) RETURN p.name, c.name;
// MATCH (p:PERSON)-[r]->(q) WHERE p.name = "孙少平" RETURN q.name, type(r);
// MATCH (a)-[r]->(b) RETURN a.name, type(r), b.name, r.evidence LIMIT 20;
