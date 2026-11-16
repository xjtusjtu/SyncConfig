# -*- coding: utf-8 -*-
"""离线自检：不联网，验证各通道的规范化与导出逻辑。

运行：python scripts/selftest.py（在本 skill 根目录或任意目录均可）
"""
import os
import sys

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(SKILL, "scripts"))

import formats
import openalex
import ncbi
import preprints
import s2api
import oa_fulltext

fails = []


def check(name, cond, detail=""):
    if cond:
        print("  ok   %s" % name)
    else:
        print("  FAIL %s %s" % (name, detail))
        fails.append(name)


print("[1] formats BibTeX 回退生成器")
rec_en = {
    "title": "Advertising and Sales Performance",
    "year": 2020,
    "venue": "Journal of Marketing Research",
    "authors": [{"name": "John Smith"}, {"name": "Jane Doe"}],
    "externalIds": {"DOI": "10.1000/xyz"},
    "volume": "57", "issue": "2", "pages": "12-30",
    "publicationTypes": ["JournalArticle"],
}
rec_zh = {
    "title": "广告强度与销售绩效",
    "year": 2021,
    "venue": "管理世界",
    "authors": [{"name": "张三"}, {"name": "李四"}],
    "externalIds": {"DOI": "10.1000/zh"},
    "publicationTypes": ["JournalArticle"],
}
bib = formats.to_bibtex([rec_en, rec_zh])
check("bib 含两条", bib.count("@article") == 2, bib)
check("bib 有 doi 字段", "10.1000/xyz" in bib)
check("bib 作者名反序", "Smith, John" in bib, bib)
check("bib key 唯一", bib.count("smith2020advertising") == 1)

print("[2] formats RIS")
ris = formats.to_ris([rec_en])
check("ris 类型 JOUR", "TY  - JOUR" in ris)
check("ris 页码拆分", "SP  - 12" in ris and "EP  - 30" in ris, ris)
check("ris 结束标记", "ER  - " in ris)

print("[3] formats APA")
apa = formats.to_apa([rec_en])
check("apa 含作者与年份", "Smith, J., & Doe, J. (2020)." in apa, apa)
check("apa 刊名后带逗号卷期", "Journal of Marketing Research, 57(2), 12-30." in apa, apa)
check("apa 含 doi 链接", "https://doi.org/10.1000/xyz" in apa, apa)

print("[4] formats GB/T 7714")
gbt, warns = formats.to_gbt([rec_en])
check("gbt 序号", gbt.strip().startswith("1."), gbt)
check("gbt 英文 et al 需 >3 人（此处 2 人不加）", "et al" not in gbt, gbt)
check("gbt 英文姓氏大写", "SMITH J" in gbt, gbt)
check("gbt 类型标记 [J]", "[J]" in gbt, gbt)
rec_many = dict(rec_en)
rec_many["authors"] = [{"name": "A One"}, {"name": "B Two"}, {"name": "C Three"},
                        {"name": "D Four"}, {"name": "E Five"}]
gbt2, _ = formats.to_gbt([rec_many])
check("gbt >3 人用 et al.", "et al" in gbt2, gbt2)
gbt3, _ = formats.to_gbt([rec_zh])
check("gbt 中文保留中文姓名", "张三" in gbt3, gbt3)
rec_zh_many = dict(rec_zh)
rec_zh_many["authors"] = [{"name": n} for n in ["张三", "李四", "王五", "赵六", "钱七"]]
gbt3b, _ = formats.to_gbt([rec_zh_many])
check("gbt 中文 >3 人用「等」", "等" in gbt3b, gbt3b)
rec_missing = {"title": "No Venue Paper", "year": None, "authors": [],
                "externalIds": {}}
gbt4, warns4 = formats.to_gbt([rec_missing])
check("gbt 缺字段产生告警", len(warns4) >= 2, warns4)
check("gbt 缺字段不编造", "DOI" not in gbt4, gbt4)

print("[5] openalex 摘要还原与规范化")
idx = {"delivery": [0], "sales": [1], "intensity": [2]}
check("倒排索引还原", openalex._restore_abstract(idx) == "delivery sales intensity")
work = {
    "id": "https://openalex.org/W123",
    "doi": "https://doi.org/10.1000/oa",
    "display_name": "An OpenAlex Work",
    "publication_year": 2022,
    "publication_date": "2022-05-01",
    "type": "article",
    "cited_by_count": 7,
    "abstract_inverted_index": idx,
    "authorships": [{"author": {"display_name": "Ada Lovelace"}}],
    "primary_location": {"landing_page_url": "https://example.org/x",
                          "source": {"display_name": "Example Journal"}},
    "open_access": {"is_oa": True, "oa_status": "gold", "oa_url": "https://example.org/p.pdf"},
    "ids": {"pmid": "pmid:123", "pmcid": "pmcid:PMC456"},
    "concepts": [{"display_name": "Marketing"}],
}
rec = openalex.normalize_work(work)
check("oa 标题", rec["title"] == "An OpenAlex Work")
check("oa 摘要", rec["abstract"] == "delivery sales intensity")
check("oa DOI 归一", rec["externalIds"]["DOI"] == "10.1000/oa")
check("oa PMID/PMCID", rec["externalIds"]["PMID"] == "123" and rec["externalIds"]["PMCID"] == "PMC456")
check("oa 期刊", rec["venue"] == "Example Journal")
check("oa 作者", rec["authors"][0]["name"] == "Ada Lovelace")
check("oa OA 字段", rec["openAccess"]["oa_status"] == "gold")

print("[6] ncbi PubMed XML 规范化")
xml = """<PubmedArticleSet><PubmedArticle>
<MedlineCitation><PMID>12345678</PMID>
<Article><Journal><Title>Test Journal</Title><ISOAbbreviation>Test J</ISOAbbreviation>
<JournalIssue><Volume>10</Volume><Issue>2</Issue><PubDate><Year>2021</Year></PubDate></JournalIssue></Journal>
<ArticleTitle>A PubMed Article</ArticleTitle>
<Pagination><MedlinePgn>100-110</MedlinePgn></Pagination>
<Abstract><AbstractText Label="BACKGROUND">Some background.</AbstractText>
<AbstractText Label="RESULTS">Some results.</AbstractText></Abstract>
<AuthorList><Author><LastName>Smith</LastName><ForeName>John</ForeName></Author>
<Author><CollectiveName>Consortium Group</CollectiveName></Author></AuthorList>
<PublicationTypeList><PublicationType>Journal Article</PublicationType></PublicationTypeList>
</Article></MedlineCitation>
<PubmedData><ArticleIdList>
<ArticleId IdType="pubmed">12345678</ArticleId>
<ArticleId IdType="doi">10.1000/pm</ArticleId>
<ArticleId IdType="pmc">PMC999</ArticleId>
</ArticleIdList></PubmedData></PubmedArticle></PubmedArticleSet>"""
import xml.etree.ElementTree as ET
node = ET.fromstring(xml).find("PubmedArticle")
rec = ncbi.normalize_pubmed(node)
check("pm 标题", rec["title"] == "A PubMed Article")
check("pm 期刊", rec["venue"] == "Test Journal")
check("pm 年份", rec["year"] == 2021)
check("pm 卷期页", rec["volume"] == "10" and rec["issue"] == "2" and rec["pages"] == "100-110")
check("pm 作者", rec["authors"][0]["name"] == "John Smith" and rec["authors"][1]["name"] == "Consortium Group")
check("pm 摘要带标签", "BACKGROUND: Some background." in rec["abstract"])
check("pm DOI/PMID/PMCID", rec["externalIds"]["DOI"] == "10.1000/pm" and
      rec["externalIds"]["PMID"] == "12345678" and rec["externalIds"]["PMCID"] == "PMC999")

print("[7] preprints arXiv Atom 规范化")
atom = """<feed xmlns="http://www.w3.org/2005/Atom">
<entry><id>http://arxiv.org/abs/2401.00001v1</id>
<published>2024-01-01T00:00:00Z</published><updated>2024-02-01T00:00:00Z</updated>
<title>An arXiv Paper</title><summary>Some abstract text.</summary>
<author><name>Alice Wang</name></author>
<doi>10.1000/arxiv</doi><journal_ref>Some Conf 2024</journal_ref>
<category term="econ.GN"/><primary_category term="econ.GN"/></entry></feed>"""
entry = ET.fromstring(atom).find("{http://www.w3.org/2005/Atom}entry")
rec = preprints.normalize_arxiv(entry)
check("arxiv id", rec["externalIds"]["ArXiv"] == "2401.00001v1")
check("arxiv 标题", rec["title"] == "An arXiv Paper")
check("arxiv 年份", rec["year"] == 2024)
check("arxiv 作者", rec["authors"][0]["name"] == "Alice Wang")
check("arxiv 期刊参考", rec["venue"] == "Some Conf 2024")
check("arxiv 类型含会议", "conference" in rec["publicationTypes"])

print("[8] s2api build_bool_query")
q = s2api.build_bool_query(phrases=["speech rate"], required=["advertising"],
                            excluded=["privacy"], alternatives=[["voice", "loudness"]])
check("bool 含短语", '"speech rate"' in q, q)
check("bool 含必含", "+advertising" in q, q)
check("bool 含排除", "-privacy" in q, q)
check("bool 含备选组", "(voice | loudness)" in q, q)

print("[9] oa_fulltext 下载计划（不执行下载）")
records = [{
    "title": "OA Paper", "externalIds": {"DOI": "10.1000/oa"},
    "openAccess": {"pdf_url": "https://example.org/a.pdf"},
    "fullTextUrls": ["https://example.org/a.txt"],
}]
plan = oa_fulltext.OAClient.build_download_plan(None, records, directory="tmp")
check("计划含两项", len(plan["items"]) == 2, plan)
check("计划记录域名", plan["items"][0]["host"] == "example.org", plan)
client = oa_fulltext.OAClient(email="test@example.org", verbose=False)
res = client.download(plan, confirm=False)
check("未确认不下载", res["status"] == "awaiting_approval", res)
check("未确认无文件产出", not os.path.isdir("tmp"), "目录不应被创建")

print("[10] econ_sources ISSN 过滤串")
import econ_sources
flt = econ_sources.EconSourcesClient(verbose=False).crossref_issn_filter(["0304-4076"])
check("ISSN 过滤串", flt == "issn:0304-4076", flt)

print("[11] nber 规范化与直链构造")
import nber as nber_mod
nber_item = {
    "title": "Learning, Sophistication, and the Returns to Advertising",
    "authors": ['<a href="/people/john_doe">John Doe</a>'],
    "displaydate": "May 2023",
    "abstract": "We study advertising.",
    "url": "/papers/w31201",
    "newthisweek": False,
}
rec = nber_mod.normalize(nber_item)
check("nber 标题", rec["title"].startswith("Learning"))
check("nber 作者去 HTML", rec["authors"][0]["name"] == "John Doe", rec["authors"])
check("nber 年份", rec["year"] == 2023)
check("nber DOI 构造", rec["externalIds"]["DOI"] == "10.3386/w31201", rec["externalIds"])
check("nber PDF 直链", rec["pdfUrl"].endswith("/w31201/w31201.pdf"), rec["pdfUrl"])
check("nber URL", rec["url"] == "https://www.nber.org/papers/w31201", rec["url"])
check("nber 类型", "working paper" in rec["publicationTypes"])

print("[12] openalex source id 常量与 pdfUrls")
check("SSRN source id", openalex.SOURCE_IDS["ssrn"] == "S4210172589")
check("NBER source id", openalex.SOURCE_IDS["nber"] == "S2809516038")
work2 = dict(work)
work2["locations"] = [{"pdf_url": "https://repo.example/a.pdf"},
                       {"landing_page_url": "https://repo.example/a"}]
work2["best_oa_location"] = {"pdf_url": "https://best.example/b.pdf"}
rec2 = openalex.normalize_work(work2)
check("pdfUrls 收集多处", len(rec2["pdfUrls"]) >= 3, rec2["pdfUrls"])

print("[13] crossref 事件字段容错")
import crossref as cr
item = {"DOI": "10.2139/ssrn.1", "title": ["T"], "event": "SSRN",
        "issued": {"date-parts": [[2020]]}}
rec3 = cr.normalize(item)
check("event 为字符串不报错", rec3["venue"] == "SSRN", rec3["venue"])

print("[14] arXiv 分类与 PDF 字段")
arxiv_rec = preprints.normalize_arxiv(entry)
check("arxiv 记录含 pdfUrls", bool(arxiv_rec.get("pdfUrls")), arxiv_rec.get("pdfUrls"))

print("[15] opencitations 规范化")
import opencitations
check("DOI 前缀补全", opencitations.normalize_id("10.1038/nature12373") == "doi:10.1038/nature12373")
check("已带前缀保持", opencitations.normalize_id("pmid:123") == "pmid:123")
blob = "omid:br/06120344846 doi:10.1038/nature12373 pmid:23903748 openalex:W2159974629"
parsed = opencitations._parse_id_blob(blob)
check("交叉标识解析 DOI", parsed.get("DOI") == "10.1038/nature12373")
check("交叉标识解析 PMID", parsed.get("PMID") == "23903748")
check("交叉标识解析 OpenAlex", parsed.get("OpenAlex") == "W2159974629")
oc_rec = opencitations._normalize_entry(
    {"oci": "a-b", "citing": blob, "cited": "doi:10.1000/xyz",
     "creation": "2013-07-31", "journal_sc": "no", "author_sc": "no"},
    "citations")
check("引用方向主记录 DOI", oc_rec["externalIds"].get("DOI") == "10.1038/nature12373")
check("引用方向对端", oc_rec["relation"]["counterpart"].get("DOI") == "10.1000/xyz")
check("引用方向标记", oc_rec["relation"]["direction"] == "citations")
oc_ref = opencitations._normalize_entry(
    {"oci": "a-b", "citing": blob, "cited": "doi:10.1000/xyz", "creation": "2013-07-31"},
    "references")
check("参考文献方向主记录是对端", oc_ref["externalIds"].get("DOI") == "10.1000/xyz")

print("[16] openalex relatedWorks")
work3 = dict(work)
work3["related_works"] = ["https://openalex.org/W111", "https://openalex.org/W222"]
work3["referenced_works"] = ["https://openalex.org/W333"]
rec4 = openalex.normalize_work(work3)
check("relatedWorks 解析", rec4["relatedWorks"] == ["W111", "W222"], rec4["relatedWorks"])
check("referencedWorks 解析", rec4["referencedWorks"] == ["W333"], rec4["referencedWorks"])

print("[17] CORE 多 key 轮流使用")
import oa_fulltext
os.environ["CORE_API_KEY_TESTPOOL1"] = "aaa"
os.environ["CORE_API_KEY_TESTPOOL2"] = "bbb"
pool = s2api.resolve_prefixed_keys("CORE_API_KEY_TESTPOOL")
check("前缀收集多个 key", pool == ["aaa", "bbb"], pool)
check("显式参数优先", s2api.resolve_prefixed_keys(
    "CORE_API_KEY_TESTPOOL", "x,y") == ["x", "y"])
for name in ("CORE_API_KEY_TESTPOOL1", "CORE_API_KEY_TESTPOOL2"):
    os.environ.pop(name, None)
oa_client = oa_fulltext.OAClient(trust_env=False, verbose=False)
oa_client.core_api_keys = ["k1", "k2"]
oa_client._core_cursor = 0
seq = [oa_client._next_core_key() for _ in range(4)]
check("key 轮转交替", seq == ["k1", "k2", "k1", "k2"], seq)

print()
if fails:
    print("失败 %d 项：%s" % (len(fails), fails))
    sys.exit(1)
print("全部离线自检通过。")
