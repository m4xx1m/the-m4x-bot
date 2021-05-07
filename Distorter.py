import io
import logging
from lottie.exporters import exporters
from lottie.importers import importers

configs = [
    [
        ["8", "4"], ["7", "4"]
    ],
    [
        ["8", "2"], ["6", "7"], ["3", "4"], ["[5]", "[0]"]
    ],
    [
        [f"[{str(cnt)}]", "[30]"] for cnt in range(30)  # ["[0]", "[30]"], ["[1]", "[30]"], ["[2]", "[30]"]
    ],
]


class Distorter:
    @staticmethod
    def tgs_to_json(input_file: bytes) -> str:
        infile = io.BytesIO(input_file)

        for p in importers:
            if 'tgs' in p.extensions:
                importer = p
                break

        outfile = io.StringIO()
        exporter = exporters.get_from_extension('json')
        an = importer.process(infile)
        exporter.process(an, outfile)
        return outfile.getvalue()

    @staticmethod
    def json_to_tgs(input_file: str) -> bytes:
        infile = io.BytesIO(input_file.encode())

        for p in importers:
            if 'json' in p.extensions:
                importer = p
                break

        outfile = io.BytesIO()
        exporter = exporters.get_from_extension('tgs')
        an = importer.process(infile)
        exporter.process(an, outfile)
        return outfile.getvalue()

    def distort(self, target: bytes, config: list):
        distorted = self.tgs_to_json(target)

        for cf in config:
            distorted = distorted.replace(cf[0], cf[1])

        outFile = io.BytesIO()
        outFile.name = "distorted.tgs"
        try:
            outFile.write(self.json_to_tgs(distorted))
        except:
            return None
        outFile.seek(0)
        return outFile

    def distorting(self, input_file: bytes, configs: list):
        return_files = []

        for conf in configs:
            try:
                distorted = self.distort(
                    target=input_file,
                    config=conf
                )
            except Exception as err:
                logging.error(f'Error in Distorter:\n{err}')
                return

            if distorted:
                return_files.append(distorted)

        return return_files
