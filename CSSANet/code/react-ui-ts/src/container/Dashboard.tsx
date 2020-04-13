import React, { Component } from "react";
import { Layout, Menu, Icon, Avatar, Badge } from "antd";
import logo from "../img/Main-Site-Logo-m.png";

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
        <Sider
          trigger={null}
          collapsible
          collapsed={this.state.collapsed}
          collapsedWidth="0"
        >
          <div className="logo">
            <img src={logo} width="110" height="45" />
          </div>
          <Menu theme="dark" mode="inline" defaultSelectedKeys={['1']} style={{textAlign:'left'}}>
            <Menu.Item key="1">
              <span style={{fontWeight:'bold'}}>MYCSSA 账户</span>
            </Menu.Item>
            <Menu.Item key="2">
              <Icon type="user" />
              <span>个人信息</span>
            </Menu.Item>
            <Menu.Item key="3">
              <Icon type="safety" />
              <span>安全与隐私</span>
            </Menu.Item>
            <Menu.Item key="4">
              <Icon type="idcard" />
              <span>我的会员卡</span>
            </Menu.Item>
            <Menu.Item key="5">
              <Icon type="appstore" />
              <span>MYCSSA应用</span>
            </Menu.Item>
            <Menu.Item key="6">
              <span>MYCSSA COMMITTE</span>
            </Menu.Item>
            <Menu.Item key="7">
              <Icon type="star" />
              <span>活动</span>
            </Menu.Item>
            <Menu.Item key="8">
              <Icon type="bars" />
              <span>稿件系统</span>
            </Menu.Item>
            <Menu.Item key="9">
              <Icon type="team" />
              <span>会员</span>
            </Menu.Item>
            <Menu.Item key="10">
              <Icon type="global" />
              <span>组织人事</span>
            </Menu.Item>
            <Menu.Item key="11">
              <Icon type="dollar" />
              <span>财务</span>
            </Menu.Item>
            <Menu.Item key="12">
              <Icon type="shop" />
              <span>商家与合作机构</span>
            </Menu.Item>
            <Menu.Item key="13">
              <Icon type="file-search" />
              <span>投稿管理</span>
            </Menu.Item>
          </Menu>
        </Sider>
        <Layout style={{ minHeight: "100vh" }}>
          <Header
            style={{
              background: "#fff",
              padding: 0,
              boxShadow: " 0 1px 4px rgba(0,21,41,.08)",
            }}
          >
            <Icon
              className="trigger"
              type={this.state.collapsed ? "menu-unfold" : "menu-fold"}
              onClick={this.toggle}
            />
            <div
              style={{
                float: "right",
                position: "relative",
                right: "90px",
                lineHeight: "64px",
              }}
            >
              <Badge count={0} showZero>
                <Icon type="notification" style={{ fontSize: "18px" }} />
              </Badge>
            </div>
            <div style={{ float: "right" }}>
              <Avatar icon="user" size="large" />
            </div>
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
          {/* <Footer
            style={{
              textAlign: "center",
              background: "#001529",
              borderTop: "1px solid lightgrey",
            }}
          >
            <span style={{ color: "white" }}> CSSA ©2020</span>
          </Footer> */}
        </Layout>
      </Layout>
    );
  }
}
