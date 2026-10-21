package lab.banking;

import java.util.List;
import java.util.Map;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class BankService {
    private final JdbcTemplate jdbc;
    private final TrainingMode training;
    public BankService(JdbcTemplate jdbc, TrainingMode training) { this.jdbc = jdbc; this.training = training; }

    public record Account(String id, String label, String balance, String currency) {}
    public record Operation(long id, String kind, String source, String destination, String amount, String note, String createdAt) {}

    public List<Account> accounts(String user) {
        return jdbc.query("SELECT * FROM accounts WHERE owner=? ORDER BY id", (rs, n) ->
            new Account(rs.getString("id"), rs.getString("label"), Money.format(rs.getLong("balance")), "USD-DEMO"), user);
    }
    public List<Operation> history(String user) {
        return jdbc.query("""
            SELECT o.* FROM operations o LEFT JOIN accounts a ON a.id=o.destination
            WHERE o.owner=? OR a.owner=? ORDER BY o.id DESC
            """, (rs, n) -> new Operation(rs.getLong("id"), rs.getString("kind"), rs.getString("source"),
                rs.getString("destination"), Money.format(rs.getLong("amount")), rs.getString("note"),
                rs.getObject("created_at", java.time.OffsetDateTime.class).toInstant().toString()), user, user);
    }

    @Transactional
    public Map<String, String> transfer(String user, String source, String destination, String amount, String note) {
        long cents = Money.cents(amount);
        // BUG-J02: únicamente en training, se permite transferir a la misma cuenta.
        if (source.equals(destination) && !training.enabled()) throw new BankError(422, "Las cuentas deben ser distintas");
        requireOwner(user, source);
        if (jdbc.queryForObject("SELECT COUNT(*) FROM accounts WHERE id=?", Integer.class, destination) == 0)
            throw new BankError(404, "Cuenta de destino no disponible");
        debit(source, cents);
        jdbc.update("UPDATE accounts SET balance=balance+? WHERE id=?", cents, destination);
        record(user, "TRANSFER", source, destination, cents, note);
        return Map.of("message", "Transferencia simulada completada", "amount", Money.format(cents));
    }

    @Transactional
    public Map<String, String> withdraw(String user, String source, String amount) {
        long cents = Money.cents(amount);
        requireOwner(user, source);
        // BUG-J01: únicamente en training, saldo exacto se rechaza incorrectamente.
        if (training.enabled() && jdbc.queryForObject("SELECT balance FROM accounts WHERE id=?", Long.class, source) == cents)
            throw new BankError(409, "Saldo insuficiente");
        debit(source, cents);
        record(user, "WITHDRAWAL", source, null, cents, "Retiro ficticio");
        return Map.of("message", "Retiro simulado completado", "amount", Money.format(cents));
    }
    private void requireOwner(String user, String source) {
        if (jdbc.queryForObject("SELECT COUNT(*) FROM accounts WHERE id=? AND owner=?", Integer.class, source, user) == 0)
            throw new BankError(404, "Cuenta de origen no disponible");
    }
    private void debit(String source, long cents) {
        if (jdbc.update("UPDATE accounts SET balance=balance-? WHERE id=? AND balance>=?", cents, source, cents) != 1)
            throw new BankError(409, "Saldo insuficiente");
    }
    private void record(String user, String kind, String source, String destination, long cents, String note) {
        jdbc.update("INSERT INTO operations(owner,kind,source,destination,amount,note) VALUES(?,?,?,?,?,?)",
                    user, kind, source, destination, cents, note);
    }
}
