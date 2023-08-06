from . import BaseExtractor


class Melongmovie(BaseExtractor):
    tag = "movie"
    host = "https://melongmovie.com"

    def extract(self, id: str) -> dict:
        """
        Ambil semua situs unduhan dan metadata dari halaman web

        Args:
              id: jalur url dimulai setelah host, type 'str'

        Returns:
              dict: hasil 'scrape' halaman web
        """

        raw = self.session.get(f"{self.host}/{id}")
        soup = self.soup(raw)

        result = {}
        for ep in soup.findAll(text=self.re.compile(r"(?i)episode\s+\d+|LINK DOWNLOAD")):
            content = ep.findNext("div")
            r = {}
            for p in content.findAll("p"):
                if p.a:
                    y = {}
                    for a in p.findAll("a"):
                        y[a.text] = a["href"]
                    title = self.re.search(r"\s*([^=]+)", p.text)
                    r[title.group(1)] = y
            result[ep] = r

        pattern = self.re.compile(r"[A-Z ]+:")
        if (ref := soup.find("strong", text=pattern)):
            for li in ref.findAllNext("li"):
                sub = "/".join(strong.text for strong in li.findAll("strong"))

                r = {}
                for a in li.findAll("a"):
                    r[a.text] = a["href"]

                title = li.findPrevious(
                    "strong", text=pattern).text.strip(": \n")
                if not result.get(title):
                    result[title] = {}
                result[title][sub] = r
        return result

    def search(self, query: str, page: int = 1) -> list:
        """
        Cari item berdasarkan 'query' yang diberikan

        Args:
              query: kata kunci pencarian, type 'str'
              page: indeks halaman web, type 'int'

        Returns:
              list: daftar item dalam bentuk 'dict'
                    dengan struktur;

                    [
                      {
                        'id':  type 'str',
                        'title': type 'str'
                      }
                    ]
        """

        raw = self.session.get(f"{self.host}/page/{page}",
                               params={"s": query})
        soup = self.soup(raw)

        result = []
        if (los := soup.find(class_="los")):
            for article in los.findAll("article"):
                a = article.find("a")
                r = {
                    "id": self.getPath(a["href"]),
                    "title": a["alt"]
                }

                for k in ("quality", "eps"):
                    if (i := article.find(class_=k)):
                        r[k] = i.text
                for ip in ("genre", "name"):
                    if (i := article.findAll(itemprop=ip)):
                        r[ip] = [a.text for a in i]
                result.append(r)
        return result
