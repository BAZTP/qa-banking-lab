package lab.banking;

import io.restassured.specification.RequestSpecification;
import org.junit.jupiter.api.*;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.jdbc.core.JdbcTemplate;
import static io.restassured.RestAssured.given;
import static org.hamcrest.Matchers.*;
import static org.junit.jupiter.api.Assertions.*;
import java.util.List;
import java.util.concurrent.*;

@SpringBootTest(webEnvironment=SpringBootTest.WebEnvironment.RANDOM_PORT,
    properties="spring.datasource.url=jdbc:h2:mem:normal-test;DB_CLOSE_DELAY=-1")
class BankApiTest {
    @LocalServerPort int port;
    @Autowired JdbcTemplate jdbc;
    String cookie;
    @BeforeEach void reset() {
        jdbc.update("DELETE FROM operations");
        jdbc.update("UPDATE accounts SET balance=CASE id WHEN 'LAB-ANA-01' THEN 100000 WHEN 'LAB-ANA-02' THEN 25000 ELSE 75000 END");
        cookie = login("ana");
    }
    String login(String username) {
        return given().port(port).contentType("application/json")
            .body("{\"username\":\""+username+"\",\"password\":\"Demo123!\"}")
            .post("/api/login").then().statusCode(200).extract().cookie("JSESSIONID");
    }
    RequestSpecification auth() { return given().port(port).cookie("JSESSIONID", cookie).header("X-Lab-Request", "1").contentType("application/json"); }
    String withdrawal(String amount) { return "{\"source\":\"LAB-ANA-01\",\"amount\":\""+amount+"\"}"; }
    String transfer(String destination) { return "{\"source\":\"LAB-ANA-01\",\"destination\":\""+destination+"\",\"amount\":\"10.25\",\"note\":\"Práctica\"}"; }
    void balances(String first, String second) {
        auth().get("/api/accounts").then().statusCode(200).body("size()", is(2)).body("[0].balance", equalTo(first)).body("[1].balance", equalTo(second));
    }
    @Test @Tag("smoke") void loginAccountsLogout() {
        given().port(port).get("/api/health").then().statusCode(200).body("trainingBugs", is(false));
        balances("1000.00", "250.00");
        auth().post("/api/logout").then().statusCode(200);
        auth().get("/api/accounts").then().statusCode(401);
        given().port(port).get("/").then().statusCode(200).body(containsString("Mini Banca Java"));
    }
    @Test @Tag("regression") void withdrawalUpdatesBalanceAndHistory() {
        auth().body(withdrawal("50.00")).post("/api/withdrawals").then().statusCode(201);
        balances("950.00", "250.00");
        auth().get("/api/history").then().body("size()", is(1)).body("[0].kind", equalTo("WITHDRAWAL")).body("[0].amount", equalTo("50.00"));
    }
    @ParameterizedTest @Tag("regression")
    @CsvSource({"0.01,201,999.99", "1000,201,0.00", "1000.01,409,1000.00", "0,422,1000.00", "-1,422,1000.00", "1.001,422,1000.00"})
    void withdrawalDataDriven(String amount, int status, String balance) {
        auth().body(withdrawal(amount)).post("/api/withdrawals").then().statusCode(status);
        balances(balance, "250.00");
        auth().get("/api/history").then().body("size()", is(status == 201 ? 1 : 0));
    }
    @Test @Tag("sanity") void transferIsAtomic() {
        auth().body(transfer("LAB-ANA-02")).post("/api/transfers").then().statusCode(201);
        balances("989.75", "260.25");
        auth().get("/api/history").then().body("size()", is(1)).body("[0].kind", equalTo("TRANSFER"));
    }
    @Test @Tag("regression") void sameAccountAndMissingDestinationAreRejected() {
        auth().body(transfer("LAB-ANA-01")).post("/api/transfers").then().statusCode(422);
        auth().body(transfer("LAB-NO-01")).post("/api/transfers").then().statusCode(404);
        balances("1000.00", "250.00");
        auth().get("/api/history").then().body("size()", is(0));
    }
    @Test @Tag("security") void invalidLoginAndUnauthenticatedRequests() {
        given().port(port).contentType("application/json").body("{\"username\":\"ana\",\"password\":\"incorrecta\"}").post("/api/login").then().statusCode(401);
        given().port(port).get("/api/accounts").then().statusCode(401);
        given().port(port).contentType("application/json").body(withdrawal("10")).post("/api/withdrawals").then().statusCode(401);
    }
    @Test @Tag("security") void cannotSpendAnotherUsersBalance() {
        cookie = login("bruno");
        auth().body(withdrawal("10")).post("/api/withdrawals").then().statusCode(404);
        auth().body(transfer("LAB-BRU-01")).post("/api/transfers").then().statusCode(404);
        auth().get("/api/accounts").then().body("size()", is(1)).body("[0].balance", equalTo("750.00"));
        auth().get("/api/history").then().body("size()", is(0));
    }
    @Test @Tag("security") void writesRequireCustomHeader() {
        given().port(port).cookie("JSESSIONID", cookie).contentType("application/json").body(withdrawal("10")).post("/api/withdrawals").then().statusCode(403);
        balances("1000.00", "250.00");
    }
    @Test @Tag("regression") void recipientSeesOnlyRelevantOperations() {
        auth().body(transfer("LAB-ANA-02")).post("/api/transfers").then().statusCode(201);
        auth().body(transfer("LAB-BRU-01")).post("/api/transfers").then().statusCode(201);
        cookie = login("bruno");
        auth().get("/api/accounts").then().body("[0].balance", equalTo("760.25"));
        auth().get("/api/history").then().body("size()", is(1)).body("[0].destination", equalTo("LAB-BRU-01"));
    }
    @Test @Tag("regression") void concurrentWithdrawalsNeverOverdraw() throws Exception {
        try (ExecutorService pool = Executors.newFixedThreadPool(2)) {
            Callable<Integer> send = () -> auth().body(withdrawal("600")).post("/api/withdrawals").statusCode();
            List<Future<Integer>> results = pool.invokeAll(List.of(send, send));
            assertEquals(List.of(201,409), results.stream().map(f -> { try { return f.get(); } catch (Exception e) { throw new RuntimeException(e); }}).sorted().toList());
        }
        balances("400.00", "250.00");
        auth().get("/api/history").then().body("size()", is(1));
    }
}
