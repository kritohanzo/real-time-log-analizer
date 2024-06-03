from django.core.management.base import BaseCommand, CommandError
from logs.models import SearchPattern, NotificationType
from datetime import datetime

BAD_BOTS = (
    "Abonti aggregator AhrefsBot Aport asterias Baiduspider BDCbot Birubot BLEXBot BUbiNG BuiltBotTough "
    "Bullseye BunnySlippers Butterfly ca\-crawler CamontSpider CCBot Cegbfeieh CheeseBot CherryPicker "
    "coccoc CopyRightCheck cosmos crawler Crescent CyotekWebCopy/1\.7 CyotekHTTP/2\.0 DeuSu discobot "
    "DittoSpyder DnyzBot DomainCrawler DotBot Download Ninja EasouSpider EmailCollector EmailSiphon "
    "EmailWolf EroCrawler Exabot ExtractorPro Ezooms FairShare Fasterfox FeedBooster Foobot Genieo "
    "GetIntent\ Crawler Gigabot gold\ crawler GrapeshotCrawler grub\-client Harvest hloader httplib "
    "HTTrack humanlinks HybridBot ia_archiver ieautodiscovery Incutio InfoNaviRobot InternetSeer "
    "IstellaBot Java Java/1\. JamesBOT JennyBot JS-Kit k2spider Kenjin Spider Keyword Density/0\.9 "
    "kmSearchBot larbin LexiBot libWeb libwww Linguee LinkExchanger LinkextractorPro linko LinkScan/8\.1a "
    "Unix LinkWalker lmspider LNSpiderguy ltx71 lwp-trivial lwp\-trivial magpie Mata Hari MaxPointCrawler "
    "MegaIndex memoryBot Microsoft URL Control MIIxpc Mippin Missigua Locator Mister PiX MJ12bot MLBot "
    "moget MSIECrawler msnbot msnbot-media NetAnts NICErsPRO Niki\-Bot NjuiceBot NPBot Nutch Offline "
    "Explorer OLEcrawler Openfind panscient\.com PostRank ProPowerBot/2\.14 ProWebWalker ptd-crawler "
    "Purebot PycURL Python\-urllib QueryN Metasearch RepoMonkey Riddler RMA Scrapy SemrushBot serf "
    "SeznamBot SISTRIX SiteBot sitecheck\.Internetseer\.com SiteSnagger Serpstat Slurp SnapPreviewBot "
    "Sogou Soup SpankBot spanner spbot Spinn3r SpyFu suggybot SurveyBot suzuran SWeb Szukacz/1\.4 "
    "Teleport Telesoft The Intraformant TheNomad TightTwatBot Titan toCrawl/UrlDispatcher True_Robot "
    "ttCrawler turingos TurnitinBot UbiCrawler UnisterBot Unknown uptime files URLy Warning User-Agent "
    "VCI Vedma Voyager WBSearchBot Web Downloader/6\.9 Web Image Collector WebAuto WebBandit WebCopier "
    "WebEnhancer WebmasterWorldForumBot WebReaper WebSauger Website Quester Webster Pro WebStripper "
    "WebZip Wget WordPress Wotbox wsr\-agent WWW\-Collector\-E Yeti YottosBot Zao Zeus ZyBORG"
)


class Command(BaseCommand):
    help = "create default search patterns"
    websocket_notification = NotificationType.objects.filter(method='websocket')
    default_search_patterns = [
        # HTTP
        {
            "name": "HTTP GET DOS", "pattern": "GET", "search_type": "SIMPLE", "counter": True,
            "count_of_events": 10, "period_of_events": datetime.strptime("00:01:00", "%H:%M:%S")
        },
        {
            "name": "HTTP INTERNAL ERROR BRUTE", "pattern": "POST 500", "search_type": "COEFFICIENT", "counter": True,
            "coefficient": 1 , "count_of_events": 3, "period_of_events": datetime.strptime("00:01:00", "%H:%M:%S")
        },
        {
            "name": "HTTP BAD BOTS", "pattern": BAD_BOTS, "search_type": "COEFFICIENT", "coefficient": 0.003
        },
        {
            "name": "HTTP GET SQL INJECTION", "pattern": "OR 1=1 \' \" SELECT FROM WHERE AND",
            "search_type": "COEFFICIENT", "coefficient": 0.375
        },
        {
            "name": "HTTP AUTH POST 400", "pattern": "POST login auth 400", "search_type": "COEFFICIENT", "coefficient": 0.75
        },
        # FTP
        {
            "name": "FTP FAILED AUTH", "pattern": "PASS 530", "search_type": "COEFFICIENT", "counter": True,
            "coefficient": 1, "count_of_events": 5, "period_of_events": datetime.strptime("00:00:30", "%H:%M:%S")
        },
        # DNS
        {
            "name": "DNS DOS", "pattern": "PACKET Rcv", "search_type": "COEFFICIENT", "counter": True,
            "coefficient": 1, "count_of_events": 10, "period_of_events": datetime.strptime("00:01:00", "%H:%M:%S")
        },
        {
            "name": "DNS DOMAIN ZONE UPDATE", "pattern": " R U ", "search_type": "SIMPLE"
        },
        {
            "name": "DNS SERVFAIL ERROR", "pattern": "SERVFAIL", "search_type": "SIMPLE"
        },
        # SMTP
        {
            "name": "SMTP RELAY DENIED", "pattern": "Relay Denied", "search_type": "SIMPLE"
        },
        {
            "name": "SMTP MARKED AS SPAM", "pattern": "marked as spam", "search_type": "SIMPLE"
        },
        {
            "name": "SMTP LINK TO BLACKLISTED", "pattern": "link to blacklisted", "search_type": "SIMPLE"
        },
        # POP
        {
            "name": "POP UNKNOWN COMMAND", "pattern": "Unknown command received", "search_type": "SIMPLE"
        },
        # FIREWALL
        {
            "name": "FIREWALL DEFAULT RULE", "pattern": "sev=warning rule=Default_Rule",
            "search_type": "COEFFICIENT", "coefficient": 1
        },
        {
            "name": "FIREWALL GERMANY RULE", "pattern": "sev=warning rule=Block_Germany",
            "search_type": "COEFFICIENT", "coefficient": 1
        },
        {
            "name": "FIREFALL ARP RESOLUTION FAILED", "pattern": "sev=warning cat=ARP",
            "search_type": "COEFFICIENT", "coefficient": 1
        },
        {
            "name": "FIREWALL BAD TCP FLAG", "pattern": "sev=notice cat=TCP_FLAG",
            "search_type": "COEFFICIENT", "coefficient": 1
        },
        {
            "name": "FIREWALL CONN DOS", "pattern": "sev=info cat=CONN event=conn_open", "counter": True,
            "search_type": "COEFFICIENT", "coefficient": 1, "count_of_events": 6,
            "period_of_events": datetime.strptime("00:01:00", "%H:%M:%S")
        },
    ]

    def handle(self, *args, **options):
        print("START CREATION DEFAULT SEARCH PATTERNS:", end=" ")
        search_patterns_exists = SearchPattern.objects.filter(
            name__in=[search_pattern.get("name") for search_pattern in self.default_search_patterns],
            pattern__in=[search_pattern.get("pattern") for search_pattern in self.default_search_patterns]
        ).exists()
        if not search_patterns_exists:
            search_patterns = SearchPattern.objects.bulk_create([SearchPattern(**fields) for fields in self.default_search_patterns])
            for search_pattern in search_patterns:
                search_pattern.notification_types.set(self.websocket_notification)
                search_pattern.save()
            print("CREATED")
        else:
            print("ALREADY EXISTS")