import json

class DiagramBuilderService:
    @staticmethod
    def build_mermaid_flowchart(nodes_and_edges):
        """
        Builds valid Mermaid.js flowchart syntax (graph TD)
        """
        lines = ["graph TD"]
        for edge in nodes_and_edges:
            src = edge.get('from', 'A').replace(' ', '_')
            dst = edge.get('to', 'B').replace(' ', '_')
            label = edge.get('label', '')
            if label:
                lines.append(f"    {src}[\"{edge.get('from')}\"] -->|\"{label}\"| {dst}[\"{edge.get('to')}\"]")
            else:
                lines.append(f"    {src}[\"{edge.get('from')}\"] --> {dst}[\"{edge.get('to')}\"]")
        return "\n".join(lines)

    @staticmethod
    def build_mermaid_mindmap(central_topic, branches):
        """
        Builds valid Mermaid.js mindmap syntax
        """
        lines = ["mindmap", f"  root(({central_topic}))"]
        for branch_name, sub_items in branches.items():
            lines.append(f"    {branch_name}")
            for item in sub_items:
                lines.append(f"      {item}")
        return "\n".join(lines)

    @staticmethod
    def build_mermaid_timeline(events):
        """
        Builds valid Mermaid.js timeline syntax
        """
        lines = ["timeline", "    title Historical Progression"]
        for ev in events:
            time_str = ev.get('time', 'Step')
            title_str = ev.get('event', 'Event')
            lines.append(f"    {time_str} : {title_str}")
        return "\n".join(lines)
