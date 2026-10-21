package lab.banking;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpSession;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.List;
import java.util.Map;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api")
public class BankController {
    private final BankService bank;
    private final TrainingMode training;
    public BankController(BankService bank, TrainingMode training) { this.bank = bank; this.training = training; }
    public record Login(@NotBlank @Size(max=50) String username, @NotBlank @Size(max=128) String password) {}
    public record Transfer(@NotBlank @Size(max=30) String source, @NotBlank @Size(max=30) String destination,
                           @NotBlank @Size(max=30) String amount, @Size(max=140) String note) {}
    public record Withdrawal(@NotBlank @Size(max=30) String source, @NotBlank @Size(max=30) String amount) {}

    @GetMapping("/health")
    public Map<String, Object> health() {
        bank.accounts("ana");
        return Map.of("status", "ok", "mode", "educational", "trainingBugs", training.enabled());
    }
    @PostMapping("/login")
    public Map<String, String> login(@Valid @RequestBody Login input, HttpServletRequest request) {
        // Credenciales públicas, solo para practicar: no es autenticación productiva.
        if (!List.of("ana", "bruno").contains(input.username()) || !MessageDigest.isEqual(
                input.password().getBytes(StandardCharsets.UTF_8), "Demo123!".getBytes(StandardCharsets.UTF_8)))
            throw new BankError(401, "Credenciales de demostración incorrectas");
        HttpSession old = request.getSession(false);
        if (old != null) old.invalidate();
        request.getSession(true).setAttribute("user", input.username());
        return Map.of("username", input.username());
    }
    @PostMapping("/logout")
    public ResponseEntity<Map<String, String>> logout(HttpServletRequest request) {
        user(request);
        request.getSession(false).invalidate();
        String cookieName = request.getServletContext().getSessionCookieConfig().getName();
        if (cookieName == null) cookieName = "JSESSIONID";
        return ResponseEntity.ok().header("Set-Cookie", cookieName + "=; Path=/; Max-Age=0; HttpOnly; SameSite=Strict")
            .body(Map.of("message", "Sesión cerrada"));
    }
    @GetMapping("/accounts")
    public List<BankService.Account> accounts(HttpServletRequest request) { return bank.accounts(user(request)); }
    @GetMapping("/history")
    public List<BankService.Operation> history(HttpServletRequest request) { return bank.history(user(request)); }
    @PostMapping("/transfers")
    public ResponseEntity<?> transfer(@Valid @RequestBody Transfer input, HttpServletRequest request) {
        return ResponseEntity.status(201).body(bank.transfer(user(request), input.source(), input.destination(), input.amount(), input.note() == null ? "" : input.note()));
    }
    @PostMapping("/withdrawals")
    public ResponseEntity<?> withdrawal(@Valid @RequestBody Withdrawal input, HttpServletRequest request) {
        return ResponseEntity.status(201).body(bank.withdraw(user(request), input.source(), input.amount()));
    }
    private String user(HttpServletRequest request) {
        HttpSession session = request.getSession(false);
        if (session == null || !(session.getAttribute("user") instanceof String)) throw new BankError(401, "Inicia sesión para continuar");
        if (!request.getMethod().equals("GET") && !"1".equals(request.getHeader("X-Lab-Request")))
            throw new BankError(403, "Falta cabecera X-Lab-Request");
        return (String) session.getAttribute("user");
    }
}
