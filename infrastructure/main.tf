resource "aws_instance" "test_server" {
  ami           = "ami-0756283460878b818"
  instance_type = "t2.micro"

  tags = {
    Name = "ExampleWebAppServer"
  }
}