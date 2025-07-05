class ResultFormatter:
    @staticmethod
    def format(total_score, breakdown):
        lines = [f"Final Score: {total_score:.2f}", "Details:"]
        for metric, info in breakdown.items():
            lines.append(
                f"- {metric}: value={info['value']}, weight={info['weight']}, weighted={info['weighted']:.2f}"
            )
        return "\n".join(lines)
