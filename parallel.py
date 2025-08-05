from multiprocessing import Pool
from main import crawl, crawl_static
from datetime import datetime
from time import time
import gc

SEEDERS = [
    # "https://www.neliti.com/journals",
    # "https://www.neliti.com/journals?page=1&per_page=100",
    # "https://www.neliti.com/journals?page=2&per_page=100",
    # "https://www.neliti.com/journals?page=3&per_page=100",
    # "https://www.neliti.com/journals?page=4&per_page=100",
    # "https://www.neliti.com/journals?page=5&per_page=100",
    # "https://www.neliti.com/journals?page=6&per_page=100",
    # "https://www.neliti.com/journals?page=7&per_page=100",
    # "https://www.neliti.com/journals?page=8&per_page=100",
    # "https://www.neliti.com/journals?page=9&per_page=100",
    # "https://www.neliti.com/journals?page=10&per_page=100",
    # "https://www.neliti.com/journals?page=11&per_page=100",
    # "https://www.neliti.com/journals?page=12&per_page=100",
    # "https://www.neliti.com/journals?page=13&per_page=100",
    # "https://www.neliti.com/journals?page=14&per_page=100",
    # "https://www.neliti.com/journals?page=15&per_page=100",
    # "https://www.neliti.com/journals?page=16&per_page=100",
    # "https://www.neliti.com/journals?page=17&per_page=100",
    # "https://www.neliti.com/journals?page=18&per_page=100",
    # "https://www.neliti.com/journals?page=19&per_page=100",
    # "https://www.neliti.com/journals?page=20&per_page=100",
    # "https://www.neliti.com/journals/eastern-european-journal-of-enterprise-technologies",
    # "https://www.neliti.com/journals/international-journal-of-health-sciences-da6f66040b3f",
    # "https://www.neliti.com/journals/journalnx",
    # "https://www.neliti.com/journals/jurnal-pendidikan-dan-pembelajaran-untan",
    # "https://www.neliti.com/journals/ijhs",
    # "https://www.neliti.com/journals/jst-ud",
    # "https://www.neliti.com/journals/ijiert",
    # "https://www.neliti.com/journals/jom-fkip-unri",
    # "https://www.neliti.com/journals/jurnal-administrasi-bisnis-s1-universitas-brawijaya",
    # "https://www.neliti.com/journals/journal-of-industrial-research-jurnal-riset-industri",
    # "https://www.neliti.com/journals/e-jurnal-manajemen-universitas-udayana",
    # "https://www.neliti.com/journals/kne-life-sciences",
    # "https://www.neliti.com/journals/jurnal-education-and-development",
    # "https://www.neliti.com/journals/jurnal-sains-dan-seni-its",
    # "https://www.neliti.com/journals/kne-social-sciences",
    # "https://www.neliti.com/journals/jom-fisip-unri",
    # "https://www.neliti.com/journals/jurnal-teknik-its",
    # "https://www.neliti.com/journals/technology-audit-and-production-reserves",
    # "https://www.neliti.com/journals/galaxy-international-interdisciplinary-research-journal",
    # "https://www.neliti.com/journals/jurnal-khatulistiwa-informatika",
    # "https://www.neliti.com/journals/ijiert",
    # "https://www.neliti.com/journals/jst-ud",
    # "https://www.neliti.com/journals/ijhs",
    # "https://www.neliti.com/journals/jom-fkip-unri",
    # "https://www.neliti.com/journals/eastern-european-journal-of-enterprise-technologies",
    # "https://www.neliti.com/journals/jurnal-administrasi-bisnis-s1-universitas-brawijaya",
    # "https://www.neliti.com/journals/jurnal-pendidikan-dan-pembelajaran-untan",
    # "https://www.neliti.com/journals/journal-of-industrial-research-jurnal-riset-industri",
    # "https://www.neliti.com/journals/journalnx",
    # "https://www.neliti.com/journals/e-jurnal-manajemen-universitas-udayana",
    # "https://www.neliti.com/journals/international-journal-of-health-sciences-da6f66040b3f",
    # "https://www.neliti.com/journals/kne-life-sciences",
    # "https://www.neliti.com/journals/jurnal-education-and-development",
    # "https://www.neliti.com/journals/jurnal-sains-dan-seni-its",
    # "https://www.neliti.com/journals/kne-social-sciences",
    # "https://www.neliti.com/journals/jom-fisip-unri",
    # "https://www.neliti.com/journals/jurnal-teknik-its",
    # "https://www.neliti.com/journals/technology-audit-and-production-reserves",
    # "https://www.neliti.com/journals/galaxy-international-interdisciplinary-research-journal",
    # "https://www.neliti.com/journals/jurnal-khatulistiwa-informatika",
    # "https://en.wikipedia.org/wiki/Main_Page",
    # "https://id.wikipedia.org/wiki/Halaman_Utama",
    # "https://www.britannica.com",
    # "https://medium.com",
    # "https://medium.com/tag/technology",
    # "https://www.kompas.com",
    # "https://www.detik.com",
    # "https://react.dev",
    # "https://news.ycombinator.com",
    # "https://stackoverflow.com/questions",
    # # "https://www.bbc.com",
    "https://www.sciencedaily.com",
    "https://www.kemdikbud.go.id",
    "https://www.researchgate.net",
    # "https://arxiv.org",
    "https://dev.to",
    # # 🧑‍💻 Forum Developer Tambahan
    # "https://www.reddit.com/r/programming/",
    # "https://www.reddit.com/r/webdev/",
    # "https://hashnode.com/",
    # "https://www.freecodecamp.org/news/",
    # "https://discuss.python.org/",
    # "https://discourse.golang.org/",
    # "https://rust-lang.zulipchat.com/",
    # "https://users.rust-lang.org/",
    # "https://developer.mozilla.org/",
    # "https://developer.android.com/",
    # "https://developer.apple.com/forums/",
    # # 📰 Portal Berita Indonesia
    "https://www.tempo.co",
    "https://www.inews.id",
    "https://www.idntimes.com",
    "https://www.jawapos.com",
    "https://www.kompas.tv",
    "https://www.tribunnews.com",
    "https://www.liputan6.com",
    "https://www.cnnindonesia.com",
    "https://www.antaranews.com",
    "https://www.suara.com",
    "https://www.merdeka.com",
]


MAX_PROCESSES = 10
MIN_PROCESSES = 5


def crawl_entry(url):
    try:
        print(f"🚀 Start crawling: {url}")
        crawl(url, depth=0, max_depth=5)
        print(f"✅ Finished crawling: {url}")
    except MemoryError:
        print(f"❌ MemoryError saat memproses {url}")
    except Exception as e:
        print(f"❌ Error saat memproses {url}: {e}")


def safe_parallel_crawl(processes: int):
    try:
        with Pool(processes=processes) as pool:
            pool.map(crawl_entry, SEEDERS)
    except MemoryError:
        print(
            f"⚠️ MemoryError dengan {processes} proses. Mengurangi dan mencoba ulang..."
        )
        gc.collect()
        if processes > MIN_PROCESSES:
            safe_parallel_crawl(processes - 1)
        else:
            print("❌ Tidak bisa mengurangi proses lebih lanjut. Gagal total.")
    except Exception as e:
        print(f"❌ Exception umum: {e}")
        raise


if __name__ == "__main__":
    start = time()
    safe_parallel_crawl(MAX_PROCESSES)
    print(f"\n⏱️ Selesai dalam {round(time() - start, 2)} detik")
