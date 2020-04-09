import React, { Component } from "react";
import { Layout, Menu, Icon } from "antd";

const { Header, Sider, Content, Footer } = Layout;

export default class Dashboard extends Component {
  state = {
    collapsed: false,
  };

  toggle = () => {
    this.setState({
      collapsed: !this.state.collapsed,
    });
  };

  render() {
    return (
      <Layout>
        <Sider trigger={null} collapsible collapsed={this.state.collapsed}>
          <div className="logo" />
          <Menu theme="dark" mode="inline" defaultSelectedKeys={["1"]}>
            <Menu.Item key="1">
              <Icon type="user" />
              <span>nav 1</span>
            </Menu.Item>
            <Menu.Item key="2">
              <Icon type="video-camera" />
              <span>nav 2</span>
            </Menu.Item>
            <Menu.Item key="3">
              <Icon type="upload" />
              <span>nav 3</span>
            </Menu.Item>
          </Menu>
        </Sider>
        <Layout style={{ minHeight: "100vh" }}>
          <Header style={{ background: "#fff", padding: 0, boxShadow: " 0 1px 4px rgba(0,21,41,.08)" }}>
            <Icon
              className="trigger"
              type={this.state.collapsed ? "menu-unfold" : "menu-fold"}
              onClick={this.toggle}
            />
          </Header>
          <Content
            style={{
              margin: "24px 16px",
              padding: 48,
              background: "#fff",
              minHeight: 280,
            }}
          >
            Content
          </Content>
          <Footer
            style={{
              textAlign: "center",
              background: "#001529",
              borderTop: "1px solid lightgrey",
            }}
          >
           <span style={{color:'white'}}> CSSA ©2020</span>
          </Footer>
        </Layout>
      </Layout>
    );
  }
}
