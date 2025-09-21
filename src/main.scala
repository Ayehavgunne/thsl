import scala.io.Source

def main(args: Array[String]): Unit =
  val file_name = "main.thsl"

  try
    val buffered_source = Source.fromFile(file_name)

    for (line <- buffered_source.getLines())
      println(line)

    buffered_source.close()
  catch
    case e: java.io.FileNotFoundException =>
      println(s"Error: File '$file_name' not found.")
    case e: Throwable =>
      println(s"An error occurred: ${e.getMessage}")
