import asyncio
import aiohttp
import json
from bs4 import BeautifulSoup
from datetime import datetime


BASE_URL = "https://markets.businessinsider.com"
INDEX_URL = "https://markets.businessinsider.com/index/components/s&p_500"
CBR_URL = "http://www.cbr.ru/scripts/XML_daily.asp"  # API Центробанка РФ для курса валют


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def get_usd_to_rub():
    """Получает текущий курс доллара к рублю с сайта ЦБ РФ."""
    async with aiohttp.ClientSession() as session:
        xml_data = await fetch(session, CBR_URL)
        soup = BeautifulSoup(xml_data, "xml")
        usd_rate = soup.find("Valute", ID="R01235").Value.text.replace(",", ".")
        return float(usd_rate)


async def parse_sp500():
    """Парсит список компаний S&P 500."""
    async with aiohttp.ClientSession() as session:
        html = await fetch(session, INDEX_URL)
        soup = BeautifulSoup(html, "lxml")
        rows = soup.select("table.table__tbody tr")

        companies = []
        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 3:
                continue

            name_tag = cols[0].find("a")
            name = name_tag.text.strip()
            url = BASE_URL + name_tag["href"]
            price_usd = float(cols[1].text.strip().replace(",", ""))
            growth = float(cols[2].text.strip().replace("%", "").replace(",", "."))

            companies.append({"name": name, "url": url, "price_usd": price_usd, "growth": growth})

        return companies


async def parse_company_details(session, company, usd_to_rub):
    """Парсит детальную информацию по компании."""
    html = await fetch(session, company["url"])
    soup = BeautifulSoup(html, "lxml")

    # Код компании
    code_tag = soup.select_one(".price-section__category")
    code = code_tag.text.split()[-1] if code_tag else "N/A"

    # P/E Ratio
    pe_tag = soup.select_one(".snapshot__value")
    pe_ratio = float(pe_tag.text.replace(",", "")) if pe_tag else None

    # 52 Week Low & High
    stats = soup.select(".snapshot__data-item")
    low, high = None, None
    for stat in stats:
        label = stat.select_one(".snapshot__label").text.strip()
        value = float(stat.select_one(".snapshot__value").text.replace(",", ""))
        if "52 Week Low" in label:
            low = value
        elif "52 Week High" in label:
            high = value

    # Вычисление потенциальной прибыли
    potential_profit = round(((high - low) / low) * 100, 2) if low and high else None

    # Конвертация в рубли
    price_rub = round(company["price_usd"] * usd_to_rub, 2)

    company.update({"code": code, "P/E": pe_ratio, "potential_profit": potential_profit, "price_rub": price_rub})
    return company


async def main():
    usd_to_rub = await get_usd_to_rub()
    companies = await parse_sp500()

    async with aiohttp.ClientSession() as session:
        tasks = [parse_company_details(session, company, usd_to_rub) for company in companies]
        companies = await asyncio.gather(*tasks)

    # Фильтрация и сортировка
    top_by_price = sorted(companies, key=lambda x: x["price_rub"], reverse=True)[:10]
    top_by_pe = sorted([c for c in companies if c["P/E"]], key=lambda x: x["P/E"])[:10]
    top_by_growth = sorted(companies, key=lambda x: x["growth"], reverse=True)[:10]
    top_by_profit = sorted([c for c in companies if c["potential_profit"]], key=lambda x: x["potential_profit"], reverse=True)[:10]

    # Сохранение в JSON
    for filename, data in [
        ("top_by_price.json", top_by_price),
        ("top_by_pe.json", top_by_pe),
        ("top_by_growth.json", top_by_growth),
        ("top_by_profit.json", top_by_profit),
    ]:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    print("Парсинг завершен. JSON файлы сохранены.")

# Запуск
if __name__ == "__main__":
    asyncio.run(main())