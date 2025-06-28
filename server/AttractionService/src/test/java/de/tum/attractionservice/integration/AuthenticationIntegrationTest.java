package de.tum.attractionservice.integration;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@AutoConfigureMockMvc
@SpringBootTest
@ActiveProfiles("test")
@DisplayName("Authentication Integration Tests")
public class AuthenticationIntegrationTest extends BaseIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    @DisplayName("连接测试 - 匿名用户可以访问")
    void connectionPing_AsAnonymous_ShouldReturnSuccess() throws Exception {
        mockMvc.perform(get("/connection/ping"))
                .andExpect(status().isOk());
    }

    @WithMockUser(username = "user", roles = {"USER"})
    @Test
    @DisplayName("用户连接测试 - 需要用户权限")
    void userPing_AsUser_ShouldReturnSuccess() throws Exception {
        mockMvc.perform(get("/connection/user-ping"))
                .andExpect(status().isOk());
    }

    @Test
    @DisplayName("用户连接测试 - 匿名用户应该被拒绝")
    void userPing_AsAnonymous_ShouldReturnUnauthorized() throws Exception {
        mockMvc.perform(get("/connection/user-ping"))
                .andExpect(status().isUnauthorized());
    }

    @WithMockUser(username = "admin", roles = {"ADMIN"})
    @Test
    @DisplayName("管理员连接测试 - 需要管理员权限")
    void adminPing_AsAdmin_ShouldReturnSuccess() throws Exception {
        mockMvc.perform(get("/connection/admin-ping"))
                .andExpect(status().isOk());
    }

    @WithMockUser(username = "user", roles = {"USER"})
    @Test
    @DisplayName("管理员连接测试 - 普通用户应该被拒绝")
    void adminPing_AsUser_ShouldReturnForbidden() throws Exception {
        mockMvc.perform(get("/connection/admin-ping"))
                .andExpect(status().isForbidden());
    }

    @Test
    @DisplayName("管理员连接测试 - 匿名用户应该被拒绝")
    void adminPing_AsAnonymous_ShouldReturnUnauthorized() throws Exception {
        mockMvc.perform(get("/connection/admin-ping"))
                .andExpect(status().isUnauthorized());
    }

    @WithMockUser(username = "manager", roles = {"MANAGER"})
    @Test
    @DisplayName("经理连接测试 - 需要经理权限")
    void managerPing_AsManager_ShouldReturnSuccess() throws Exception {
        mockMvc.perform(get("/connection/manager-ping"))
                .andExpect(status().isOk());
    }
}
