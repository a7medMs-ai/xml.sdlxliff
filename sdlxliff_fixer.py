# Final version: all logic correct AND no pretty_print (to preserve SDLXLIFF internal structure)
from lxml import etree
import io
from copy import deepcopy

# Namespace definitions
ns = {
    "x": "urn:oasis:names:tc:xliff:document:1.2",
    "sdl": "http://sdl.com/FileTypes/SdlXliff/1.0"
}

def parse_sdlxliff(file_content):
    """Parse the SDLXLIFF XML content into an lxml tree."""
    try:
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.fromstring(file_content, parser)
        return tree
    except etree.XMLSyntaxError as e:
        raise ValueError(f"Invalid SDLXLIFF format: {str(e)}")

def find_trans_unit_map(tree):
    """Create a mapping of trans-unit elements by their id."""
    return {
        tu.attrib.get("id").strip(): tu
        for tu in tree.xpath(".//x:trans-unit", namespaces=ns)
        if tu.attrib.get("id")
    }

def get_normalized_text(element):
    """Extract and normalize all inner text from an XML element (as string)."""
    return etree.tostring(element, encoding="unicode", with_tail=False, method="xml").strip() if element is not None else ""

def contains_locked_xid(element):
    """Check if element contains locked x-id or locked id indicating structure."""
    if element is None:
        return False
    xml = etree.tostring(element, encoding="unicode")
    return 'xid="lockTU' in xml or 'id="locked' in xml

def replace_target_safely(clean_tu, damaged_target, clean_target):
    """Replace <target> in a way compatible with System.Xml (XmlElement only)."""
    idx = list(clean_tu).index(clean_target)
    clean_tu.remove(clean_target)

    new_target = etree.Element("{urn:oasis:names:tc:xliff:document:1.2}target")

    # Copy attributes
    for attr in damaged_target.attrib:
        new_target.set(attr, damaged_target.attrib[attr])

    # If the original contains text only
    if damaged_target.text and not list(damaged_target):
        new_target.text = damaged_target.text
    else:
        # Copy full structure
        for child in damaged_target:
            new_target.append(deepcopy(child))
        new_target.text = damaged_target.text

    clean_tu.insert(idx, new_target)

def fix_sdlxliff(clean_tree, damaged_tree):
    """Smart and safe replacement of <target> and <sdl:seg-defs>."""
    clean_units = find_trans_unit_map(clean_tree)
    damaged_units = find_trans_unit_map(damaged_tree)
    replacements_done = []

    for tu_id, clean_tu in clean_units.items():
        if tu_id in damaged_units:
            damaged_tu = damaged_units[tu_id]

            # Elements
            damaged_target = damaged_tu.find("x:target", namespaces=ns)
            clean_target = clean_tu.find("x:target", namespaces=ns)
            src_text = get_normalized_text(damaged_tu.find("x:source", namespaces=ns))
            seg_text = get_normalized_text(damaged_tu.find("x:seg-source", namespaces=ns))
            tgt_text = get_normalized_text(damaged_target)

            if damaged_target is not None and not contains_locked_xid(damaged_target):
                if tgt_text.strip() != "" and tgt_text not in [src_text, seg_text]:
                    if clean_target is not None:
                        replace_target_safely(clean_tu, damaged_target, clean_target)
                        replacements_done.append(f"{tu_id}: target")

            # Always update seg-defs if present
            clean_segdefs = clean_tu.find("sdl:seg-defs", namespaces=ns)
            damaged_segdefs = damaged_tu.find("sdl:seg-defs", namespaces=ns)
            if clean_segdefs is not None and damaged_segdefs is not None:
                idx = list(clean_tu).index(clean_segdefs)
                clean_tu.remove(clean_segdefs)
                clean_tu.insert(idx, deepcopy(damaged_segdefs))
                replacements_done.append(f"{tu_id}: seg-defs")

    print(f"Total replacements made: {len(replacements_done)}")
    return clean_tree

def save_fixed_file(tree, original_name):
    """Save file in raw XML format (no pretty print) to avoid corrupting SDLXLIFF structure."""
    fixed_name = f"fixed_{original_name}"
    content = etree.tostring(tree, xml_declaration=True, encoding="UTF-8")
    return io.BytesIO(content), fixed_name
