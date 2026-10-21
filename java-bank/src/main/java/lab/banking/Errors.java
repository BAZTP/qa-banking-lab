package lab.banking;

import java.util.Map;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.annotation.*;

@RestControllerAdvice
public class Errors {
    @ExceptionHandler(BankError.class)
    ResponseEntity<?> business(BankError error) { return ResponseEntity.status(error.status).body(Map.of("detail", error.getMessage())); }
    @ExceptionHandler({MethodArgumentNotValidException.class, HttpMessageNotReadableException.class})
    ResponseEntity<?> validation(Exception error) { return ResponseEntity.unprocessableEntity().body(Map.of("detail", "Revisa los datos introducidos")); }
}
