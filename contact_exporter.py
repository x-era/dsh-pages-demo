"""Export fictional contacts to CSV using the Python standard library."""

from collections.abc import Iterable, Mapping
import csv
import io


def export_contacts(contacts: Iterable[Mapping[str, str]]) -> str:
    """Return a CSV document with name and postal_code columns."""
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(("name", "postal_code"))
    for contact in contacts:
        # Postal codes are identifiers, so preserve leading zeroes.
        postal_code = str(contact["postal_code"])
        writer.writerow((contact["name"], postal_code))
    return output.getvalue()
