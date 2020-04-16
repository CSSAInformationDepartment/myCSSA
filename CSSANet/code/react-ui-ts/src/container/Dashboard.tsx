import React, { Component } from "react";
import { Layout, Menu, Icon, Avatar, Badge } from "antd";
import logo from "../img/Main-Site-Logo-m.png";

const { Header, Sider, Content } = Layout;
const { SubMenu } = Menu;

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
          <Menu
            theme="dark"
            mode="inline"
            defaultSelectedKeys={["1"]}
            style={{ textAlign: "left" }}
          >
            <Menu.Item key="1">
              <span style={{ fontWeight: "bold" }}>MYCSSA 账户</span>
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
            <SubMenu
              key="5"
              title={
                <span>
                  <Icon type="appstore" />
                  <span>MYCSSA应用</span>
                </span>
              }
            >
              <Menu.Item key="51">
                <Icon type="barcode" />
                <span>活动票务</span>
              </Menu.Item>
              <Menu.Item key="52">
                <Icon type="sound" />
                <span>求职招聘</span>
              </Menu.Item>
            </SubMenu>

            <Menu.Item key="6">
              <span>MYCSSA COMMITTE</span>
            </Menu.Item>

            <SubMenu
              key="7"
              title={
                <span>
                  <Icon type="star" />
                  <span>活动</span>
                </span>
              }
            >
              <Menu.Item key="71">
                <Icon type="form" />
                <span>活动计划</span>
              </Menu.Item>
              <Menu.Item key="72">
                <Icon type="file-text" />
                <span>信息收集</span>
              </Menu.Item>
              <Menu.Item key="73">
                <Icon type="profile" />
                <span>报名管理</span>
              </Menu.Item>
              <Menu.Item key="74">
                <Icon type="edit" />
                <span>活动签到</span>
              </Menu.Item>
              <Menu.Item key="75">
                <Icon type="gift" />
                <span>活动抽奖</span>
              </Menu.Item>
            </SubMenu>

            <SubMenu
              key="8"
              title={
                <span>
                  <Icon type="bars" />
                  <span>稿件系统</span>
                </span>
              }
            >
              <Menu.Item key="81">
                <Icon type="ordered-list" />
                <span>稿件列表</span>
              </Menu.Item>
              <Menu.Item key="82">
                <Icon type="cloud-upload" />
                <span>发布稿件</span>
              </Menu.Item>
              <Menu.Item key="83">
                <Icon type="check" />
                <span>审阅稿件</span>
              </Menu.Item>
            </SubMenu>

            <SubMenu
              key="9"
              title={
                <span>
                  <Icon type="team" />
                  <span>会员</span>
                </span>
              }
            >
              <Menu.Item key="91">
                <Icon type="credit-card" />
                <span>会员激活</span>
              </Menu.Item>
              <Menu.Item key="92">
                <Icon type="search" />
                <span>信息管理</span>
              </Menu.Item>
            </SubMenu>

            <SubMenu
              key="10"
              title={
                <span>
                  <Icon type="global" />
                  <span>组织人事</span>
                </span>
              }
            >
              <Menu.Item key="101">
                <Icon type="usergroup-add" />
                <span>部门人事</span>
              </Menu.Item>
              <Menu.Item key="102">
                <Icon type="user-add" />
                <span>纳新管理</span>
              </Menu.Item>
              <Menu.Item key="103">
                <Icon type="solution" />
                <span>岗位发布</span>
              </Menu.Item>
              <Menu.Item key="104">
                <Icon type="schedule" />
                <span>日程表</span>
              </Menu.Item>
            </SubMenu>

            <SubMenu
              key="11"
              title={
                <span>
                  <Icon type="dollar" />
                  <span>财务</span>
                </span>
              }
            >
              <Menu.Item key="111">
                <Icon type="trademark" />
                <span>交易流水</span>
              </Menu.Item>
              <Menu.Item key="112">
                <Icon type="highlight" />
                <span>报销申请</span>
              </Menu.Item>
              <Menu.Item key="113">
                <Icon type="money-collect" />
                <span>收款核查</span>
              </Menu.Item>
              <Menu.Item key="114">
                <Icon type="audit" />
                <span>报销核查</span>
              </Menu.Item>
            </SubMenu>

            <SubMenu
              key="12"
              title={
                <span>
                  <Icon type="shop" />
                  <span>合作商家</span>
                </span>
              }
            >
              <Menu.Item key="121">
                <Icon type="unordered-list" />
                <span>商家总览</span>
              </Menu.Item>
              <Menu.Item key="122">
                <Icon type="plus-circle" />
                <span>新增商家</span>
              </Menu.Item>
            </SubMenu>

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
