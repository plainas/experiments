import json
import sys
from lxml import etree



def _get_text_by_xpath(root, namespaces, xpath):
    el = root.find(xpath, namespaces=namespaces)
    return el.text.strip() if el is not None and el.text else None

def parse_procurement_xml(xml_content, datasource="TENDSIGN"):
    root = etree.fromstring(xml_content.encode("utf-8"))
    ns = {
        "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
        "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
        "efac": "http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1",
    }

    buyer_name = _get_text_by_xpath(root, ns, ".//efac:Company/cac:PartyName/cbc:Name")
    org_number = _get_text_by_xpath(root, ns, ".//efac:Company/cac:PartyLegalEntity/cbc:CompanyID")

    title = _get_text_by_xpath(root, ns, ".//cac:ProcurementProject/cbc:Name")
    description = _get_text_by_xpath(root, ns, ".//cac:ProcurementProject/cbc:Description")
    reference_number = _get_text_by_xpath(root, ns, ".//cac:ProcurementProject/cbc:ID")

    document_url = _get_text_by_xpath(root, ns, ".//cac:CallForTendersDocumentReference//cbc:URI")
    submission_url = _get_text_by_xpath(root, ns, ".//cac:TenderRecipientParty/cbc:EndpointID")

    issue_date = _get_text_by_xpath(root, ns, ".//cbc:IssueDate")
    deadline = _get_text_by_xpath(root, ns, ".//cac:TenderSubmissionDeadlinePeriod/cbc:EndDate")

    lots = []
    for lot in root.findall(".//cac:ProcurementProjectLot", namespaces=ns):
        lot_id = lot.find("cbc:ID", namespaces=ns)
        lot_name = lot.find(".//cbc:Name", namespaces=ns)

        lots.append({
            "id": lot_id.text if lot_id is not None else None,
            "name": lot_name.text if lot_name is not None else None
        })

    return {
        "buyer": {
            "name": buyer_name,
            "organisationNumber": org_number
        },
        "datasource": datasource,
        "date": f"{issue_date}T00:00:00.000Z" if issue_date else None,
        "tender": {
            "title": title,
            "description": description,
            "documentUrl": document_url,
            "submissionUrl": submission_url,
            "referenceNumber": reference_number,
            "submissionDeadline": f"{deadline}T00:00:00.000Z" if deadline else None
        },
        "lots": lots
    }


# Just for quick testing, pass the filename as a cli arg
if __name__ == "__main__":
    xml_filename = sys.argv[1]
    xml_text = open(xml_filename, "r", encoding="utf-8").read()
    result = parse_procurement_xml(xml_text,datasource=xml_filename)
    print(json.dumps(result, indent=2, ensure_ascii=False))