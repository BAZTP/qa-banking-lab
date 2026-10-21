package lab.banking;

import org.junit.jupiter.api.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.ActiveProfiles;
import static io.restassured.RestAssured.given;
import static org.hamcrest.Matchers.*;

/** Estas pruebas verifican que los defectos didácticos se pueden reproducir;
 * no afirman que el comportamiento defectuoso cumpla el negocio. */
@ActiveProfiles("training")
@SpringBootTest(webEnvironment=SpringBootTest.WebEnvironment.RANDOM_PORT, properties="lab.training-bugs=true")
class TrainingBugsTest {
    @LocalServerPort int port;
    @Autowired JdbcTemplate jdbc;
    String cookie;
    @BeforeEach void reset() {
        jdbc.update("DELETE FROM operations");
        jdbc.update("UPDATE accounts SET balance=100000 WHERE id='LAB-ANA-01'");
        cookie = given().port(port).contentType("application/json").body("{\"username\":\"ana\",\"password\":\"Demo123!\"}")
            .post("/api/login").then().statusCode(200).extract().cookie("TRAININGSESSION");
    }
    @Test void reproducesBugJ01ExactBalanceWronglyRejected() {
        given().port(port).get("/api/health").then().body("trainingBugs", is(true));
        given().port(port).cookie("TRAININGSESSION",cookie).header("X-Lab-Request","1").contentType("application/json")
            .body("{\"source\":\"LAB-ANA-01\",\"amount\":\"1000.00\"}").post("/api/withdrawals").then().statusCode(409);
    }
    @Test void reproducesBugJ02SameAccountIncorrectlyAccepted() {
        given().port(port).cookie("TRAININGSESSION",cookie).header("X-Lab-Request","1").contentType("application/json")
            .body("{\"source\":\"LAB-ANA-01\",\"destination\":\"LAB-ANA-01\",\"amount\":\"10.00\"}").post("/api/transfers").then().statusCode(201);
    }
}
