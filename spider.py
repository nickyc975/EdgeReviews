import json
import urllib3


class ReviewsGetter(object):
    # 每次最多获取的评论数，不要超过10
    MAX_PAGE_SIZE = 10

    # 获取扩展的产品ID（Product ID）的链接
    PRODUCT_ID_URL_BASE = "https://microsoftedge.microsoft.com/addons/getproductdetailsbycrxid/"

    # 获取所有上架地区的名称及代码
    REGIONS_URL = "https://microsoftedge.microsoft.com/Assets/Regions/NativeRegions-zh-CN.json"

    # 获取评论的链接
    REVIEWS_URL_BASE = "https://ratingsedge.rnr.microsoft.com/v1.0/ratingsedge/product/"

    # 获取评论的请求头
    REVIEWS_HEADERS = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36"
    }

    def __init__(self, crx_id):
        self.crx_id = crx_id
        self.http = urllib3.PoolManager()

        response = json.loads(
            self.http.request("GET", self.PRODUCT_ID_URL_BASE + self.crx_id).data.decode("utf-8")
        )

        self.reviews_url = self.REVIEWS_URL_BASE + response["storeProductId"]
        self.regions = json.loads(
            self.http.request("GET", self.REGIONS_URL).data.decode("utf-8")
        )

    def get_reviews_by(self, region_code, page_size, skip_items=0):
        """
        获取某一地区的特定评价

        :param region_code: 地区码
        :param page_size: 需要获取的评价个数
        :param skip_items: 需要跳过的评价个数
        """
        response = self.http.request(
            "GET",
            self.reviews_url,
            fields={
                "catalogId": 1,
                "market": region_code,
                "locale": "zh-CN",
                "callSiteId": 3,
                "pageSize": page_size,
                "orderBy": 1,
                "skipItems": skip_items
            },
            headers=self.REVIEWS_HEADERS
        )
        return json.loads(response.data.decode("utf-8"))

    def get_reviews(self):
        """
        获取一个扩展的所有评价
        """
        reviews = []
        for region_code, region_name in self.regions.items():
            print(f"Getting reviews in {region_name}...")

            reviews_got = 0
            reviews_total = self.get_reviews_by(region_code, 1)["PagingInfo"]["TotalItems"]

            while reviews_total > reviews_got:
                page_size = min(reviews_total - reviews_got, self.MAX_PAGE_SIZE)
                raw_reviews = self.get_reviews_by(region_code, page_size, reviews_got)
                reviews_got += page_size

                if "Items" not in raw_reviews.keys():
                    print("Error:", raw_reviews)
                    break

                for raw_review in raw_reviews["Items"]:
                    # (地区名, 用户名, 提交时间, 评分, 评价内容)
                    reviews.append(
                        (region_name, raw_review["UserName"], raw_review["SubmittedDateTime"], raw_review["Rating"], raw_review["ReviewText"])
                    )
        return reviews

    def save_reviews(self, filename):
        reviews = self.get_reviews()
        with open(filename, "w") as f:
            f.write("|地区|用户|时间|评分|评价|\n")
            f.write("|:-:|:-:|:-:|:-:|:-|\n")
            for review in reviews:
                review_time = review[2].split(".")[0].replace("T", " ")
                review_text = review[4].replace("\r", "").replace("\n", " ")
                f.write(f"|{review[0]}|{review[1]}|{review_time}|{review[3]}|{review_text}|\n")


if __name__ == "__main__":
    getter = ReviewsGetter("bfdogplmndidlpjfhoijckpakkdjkkil")
    getter.save_reviews("reviews.md")
