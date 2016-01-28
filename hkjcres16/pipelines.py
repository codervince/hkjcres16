from scrapy import signals
from scrapy.exporters import CsvItemExporter


class Hkjcres16Pipeline(object):
    def process_item(self, item, spider):
        return item


class CsvExportPipeline(object):
    def __init__(self, filename, fields_to_export):
        self.filename = filename
        self.fields_to_export = fields_to_export

        self.csv_file = None
        self.csv_exporter = None

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls(
            crawler.settings.get('OUTPUT_FILE_NAME'),
            crawler.settings.get('CSV_EXPORT_PIPELINE_FIELDS'),
        )
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline

    def spider_opened(self, spider):
        self.csv_file = open(self.filename, 'w')

        self.csv_exporter = CsvItemExporter(self.csv_file, fields_to_export=self.fields_to_export)
        self.csv_exporter.start_exporting()

    def spider_closed(self, spider):
        self.csv_exporter.finish_exporting()
        self.csv_file.close()

    def process_item(self, item, spider):
        item_type = type(item).__name__

        if item_type == 'HorseItem':
            item_dict = {}

            for key, value in item['hkjcres16_item'][0].items():
                item_dict['Hkjcres16Item__' + key] = value

            for key, value in item.items():
                item_dict['HorseItem__' + key] = value

            self.csv_exporter.export_item(item_dict)
        else:
            pass
            # exporter.export_item(item)

        return item
