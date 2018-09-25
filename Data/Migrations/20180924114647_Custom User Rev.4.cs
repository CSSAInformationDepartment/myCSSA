using System;
using Microsoft.EntityFrameworkCore.Migrations;

namespace myCSSA.Data.Migrations
{
    public partial class CustomUserRev4 : Migration
    {
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.AddColumn<string>(
                name: "Discriminator",
                table: "AspNetUsers",
                nullable: false,
                defaultValue: "");

            migrationBuilder.AddColumn<int>(
                name: "DeptId",
                table: "AspNetUsers",
                nullable: true);

            migrationBuilder.AddColumn<DateTime>(
                name: "JoinDate",
                table: "AspNetUsers",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "PositionId",
                table: "AspNetUsers",
                nullable: true);

            migrationBuilder.AddColumn<int>(
                name: "academicId",
                table: "AspNetUsers",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "gender",
                table: "AspNetUsers",
                maxLength: 1,
                nullable: true);

            migrationBuilder.AddColumn<bool>(
                name: "isActivated",
                table: "AspNetUsers",
                nullable: true);

            migrationBuilder.AddColumn<bool>(
                name: "isAuthenticated",
                table: "AspNetUsers",
                nullable: true);

            migrationBuilder.AddColumn<string>(
                name: "studentId",
                table: "AspNetUsers",
                maxLength: 6,
                nullable: true);

            migrationBuilder.CreateTable(
                name: "uniMajors",
                columns: table => new
                {
                    uniMajorId = table.Column<int>(nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    MajorName = table.Column<string>(nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_uniMajors", x => x.uniMajorId);
                });

            migrationBuilder.CreateTable(
                name: "userContacts",
                columns: table => new
                {
                    ContactRecId = table.Column<int>(nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    telNumber = table.Column<string>(nullable: false),
                    address = table.Column<string>(nullable: false),
                    originate = table.Column<string>(nullable: false),
                    postcode = table.Column<string>(maxLength: 4, nullable: true),
                    userId = table.Column<int>(nullable: false),
                    ApplicationUserId = table.Column<string>(nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_userContacts", x => x.ContactRecId);
                    table.ForeignKey(
                        name: "FK_userContacts_AspNetUsers_ApplicationUserId",
                        column: x => x.ApplicationUserId,
                        principalTable: "AspNetUsers",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });

            migrationBuilder.CreateTable(
                name: "userDepartments",
                columns: table => new
                {
                    DeptId = table.Column<int>(nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    DeptName = table.Column<string>(nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_userDepartments", x => x.DeptId);
                });

            migrationBuilder.CreateTable(
                name: "userJobPositions",
                columns: table => new
                {
                    PositionId = table.Column<int>(nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    PositionName = table.Column<string>(nullable: true)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_userJobPositions", x => x.PositionId);
                });

            migrationBuilder.CreateTable(
                name: "userAcademicInfos",
                columns: table => new
                {
                    academicId = table.Column<int>(nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    timeOfCreate = table.Column<DateTime>(nullable: false),
                    userId = table.Column<int>(nullable: false),
                    uniMajorId = table.Column<int>(nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_userAcademicInfos", x => x.academicId);
                    table.ForeignKey(
                        name: "FK_userAcademicInfos_uniMajors_uniMajorId",
                        column: x => x.uniMajorId,
                        principalTable: "uniMajors",
                        principalColumn: "uniMajorId",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_AspNetUsers_DeptId",
                table: "AspNetUsers",
                column: "DeptId");

            migrationBuilder.CreateIndex(
                name: "IX_AspNetUsers_PositionId",
                table: "AspNetUsers",
                column: "PositionId");

            migrationBuilder.CreateIndex(
                name: "IX_AspNetUsers_academicId",
                table: "AspNetUsers",
                column: "academicId",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_userAcademicInfos_uniMajorId",
                table: "userAcademicInfos",
                column: "uniMajorId");

            migrationBuilder.CreateIndex(
                name: "IX_userContacts_ApplicationUserId",
                table: "userContacts",
                column: "ApplicationUserId");

            migrationBuilder.AddForeignKey(
                name: "FK_AspNetUsers_userDepartments_DeptId",
                table: "AspNetUsers",
                column: "DeptId",
                principalTable: "userDepartments",
                principalColumn: "DeptId",
                onDelete: ReferentialAction.Cascade);

            migrationBuilder.AddForeignKey(
                name: "FK_AspNetUsers_userJobPositions_PositionId",
                table: "AspNetUsers",
                column: "PositionId",
                principalTable: "userJobPositions",
                principalColumn: "PositionId",
                onDelete: ReferentialAction.Cascade);

            migrationBuilder.AddForeignKey(
                name: "FK_AspNetUsers_userAcademicInfos_academicId",
                table: "AspNetUsers",
                column: "academicId",
                principalTable: "userAcademicInfos",
                principalColumn: "academicId",
                onDelete: ReferentialAction.Cascade);
        }

        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropForeignKey(
                name: "FK_AspNetUsers_userDepartments_DeptId",
                table: "AspNetUsers");

            migrationBuilder.DropForeignKey(
                name: "FK_AspNetUsers_userJobPositions_PositionId",
                table: "AspNetUsers");

            migrationBuilder.DropForeignKey(
                name: "FK_AspNetUsers_userAcademicInfos_academicId",
                table: "AspNetUsers");

            migrationBuilder.DropTable(
                name: "userAcademicInfos");

            migrationBuilder.DropTable(
                name: "userContacts");

            migrationBuilder.DropTable(
                name: "userDepartments");

            migrationBuilder.DropTable(
                name: "userJobPositions");

            migrationBuilder.DropTable(
                name: "uniMajors");

            migrationBuilder.DropIndex(
                name: "IX_AspNetUsers_DeptId",
                table: "AspNetUsers");

            migrationBuilder.DropIndex(
                name: "IX_AspNetUsers_PositionId",
                table: "AspNetUsers");

            migrationBuilder.DropIndex(
                name: "IX_AspNetUsers_academicId",
                table: "AspNetUsers");

            migrationBuilder.DropColumn(
                name: "Discriminator",
                table: "AspNetUsers");

            migrationBuilder.DropColumn(
                name: "DeptId",
                table: "AspNetUsers");

            migrationBuilder.DropColumn(
                name: "JoinDate",
                table: "AspNetUsers");

            migrationBuilder.DropColumn(
                name: "PositionId",
                table: "AspNetUsers");

            migrationBuilder.DropColumn(
                name: "academicId",
                table: "AspNetUsers");

            migrationBuilder.DropColumn(
                name: "gender",
                table: "AspNetUsers");

            migrationBuilder.DropColumn(
                name: "isActivated",
                table: "AspNetUsers");

            migrationBuilder.DropColumn(
                name: "isAuthenticated",
                table: "AspNetUsers");

            migrationBuilder.DropColumn(
                name: "studentId",
                table: "AspNetUsers");
        }
    }
}
