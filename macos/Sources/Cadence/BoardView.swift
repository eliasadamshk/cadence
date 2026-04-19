import SwiftUI

struct BoardView: View {
    let board: Board

    var body: some View {
        HStack(alignment: .top, spacing: 10) {
            ForEach(board.columns) { column in
                columnView(column)
            }
        }
    }

    private func columnView(_ column: Column) -> some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(spacing: 6) {
                Circle()
                    .fill(Theme.columnColors[column.id] ?? Theme.textTertiary)
                    .frame(width: 6, height: 6)
                Text(column.name)
                    .font(.system(size: 10, weight: .semibold))
                    .foregroundStyle(Theme.textSecondary)
                    .textCase(.uppercase)
                    .tracking(0.3)
                    .lineLimit(1)
                Spacer()
                Text("\(column.cards.count)")
                    .font(.system(size: 9, weight: .medium, design: .monospaced))
                    .foregroundStyle(Theme.textTertiary)
            }
            .padding(.bottom, 2)

            if column.cards.isEmpty {
                RoundedRectangle(cornerRadius: Theme.cardRadius)
                    .fill(Theme.columnBgs[column.id] ?? Theme.surface)
                    .frame(height: 32)
                    .opacity(0.5)
            } else {
                ForEach(column.cards) { card in
                    cardView(card, columnId: column.id)
                }
            }

            Spacer(minLength: 0)
        }
        .frame(maxWidth: .infinity)
    }

    private func cardView(_ card: Card, columnId: String) -> some View {
        VStack(alignment: .leading, spacing: 3) {
            Text(card.title)
                .font(.system(size: 11, weight: .regular))
                .foregroundStyle(Theme.text)
                .lineLimit(2)
            if let assignee = card.assignee {
                Text(assignee)
                    .font(.system(size: 10, weight: .regular))
                    .foregroundStyle(Theme.textTertiary)
            }
        }
        .padding(.horizontal, 8)
        .padding(.vertical, 7)
        .frame(maxWidth: .infinity, alignment: .leading)
        .background(Theme.columnBgs[columnId] ?? Theme.surface)
        .clipShape(RoundedRectangle(cornerRadius: Theme.cardRadius))
    }
}
