/*
This script crawls and archives thepiratebay's public content.
Torrent info is saved in plain text which are grouped in zip
archives.
Categories are saved in categories.txt

Author:
Pedro ( http://lamehacks.net )

Format:
NAME<newline>
HASH<neline>
CATEGORY<neline>
<newline>
INFO
<endoffile>

In memory of Fravia ( http://search.lores.eu/ )
*/
import scala.actors.Actor
import scala.actors.Actor._
import actors.TIMEOUT
import scala.io.Source
import java.net.URL
import scala.util.matching.Regex
import scala.collection.mutable.HashMap
import scala.collection.mutable.Queue
import java.util.zip.ZipOutputStream
import java.io._
import java.util.zip.{ ZipEntry, ZipOutputStream }
import java.util.Calendar
import java.text.SimpleDateFormat


case class Torrent(title:String,hash:String, nfo:String,category:Int)
case class Category(id:Int,name:String)
case class ChunkInfo(size:Int, offset:Int)
case class Filename(filename:String)


val initialId :Int = 3219950 //id of the oldest torrent
val maxId : Int =    getNewestTorrentId
val chunkSize : Int = 400
val chunkTimeout: Int = 10000 //not used
val archiveNumFiles : Int = 4000
var zipNumber : Int = 0

var catActor = new CategoriesActor
var bigBoss = new BigBossActor

catActor.start
bigBoss.start

bigBoss ! new ChunkInfo(chunkSize, initialId)


def parse(pageContent:String): Torrent = {  
  val pageRegex = """(?s).*?title">(.*?)<.*?href="/browse/(\d+)".*?category">(.*?)<.*?href="magnet:(.*?)".*?class="nfo">.*?<pre>(.*?)</pre>.*?</div>.*?""".r
  val hashRegex = """.*?btih:([0-9a-f]+)&.*?""".r
  var pageRegex(title,catnum, cat,magnetUrl,nfo) = pageContent
  var hashRegex(hash) = magnetUrl
  catActor ! Category(catnum.toInt, cat)
  return Torrent(title.trim,hash,nfo.trim,catnum.toInt)
}

def getNewestTorrentId(): Int = {
  val connection = new URL("http://thepiratebay.se/recent").openConnection
  val pageContent = Source.fromInputStream(connection.getInputStream).getLines.mkString("\n")
  """\d+""".r.findFirstIn("""href="/torrent/(\d+)/""".r.findFirstIn(pageContent).get).get.toInt
}

class BigBossActor() extends Actor{
  var filenamesQueue = Queue.empty[String]
  
  def act{
      while(true){
        //receiveWithin(chunkTimeout){ //WTF? https://issues.scala-lang.org/browse/SI-5460
          receive{
          case chunkInfo : ChunkInfo =>{
            if (chunkInfo.offset <= maxId){
              archive
              new MediatorActor(this, chunkInfo) start
            }else{
              archive
              zip((zipNumber.toString).reverse.padTo(5,"0").reverse.mkString +".zip",filenamesQueue)
              catActor ! "save"
              return
            }
          }
          case filename : Filename => filenamesQueue enqueue filename.filename
        }
      }
  }

  
  def archive(){
    while (filenamesQueue.length > archiveNumFiles){
      println("\nZipping...")
      var filesToZip = (0 to (archiveNumFiles-1)).map{_=>filenamesQueue.dequeue}
      //var zipFileName = new SimpleDateFormat("yyyyMMddHHmm") format Calendar.getInstance.getTime
      var zipFileName = (zipNumber.toString).reverse.padTo(5,"0").reverse.mkString +".zip"
      zipNumber = zipNumber+1
      zip(zipFileName, filesToZip);
      println("\nDone Zipping...")
    }
  }
  

  def zip(out: String, files: Iterable[String]) = {
      val zip = new ZipOutputStream(new FileOutputStream(out))
      files.foreach { name =>
        zip.putNextEntry(new ZipEntry(name))
        val in = new BufferedInputStream(new FileInputStream(name))
        var b = in.read()
        while (b > -1) {
          zip.write(b)
          b = in.read()
        }
        in.close()
        zip.closeEntry()
        new java.io.File(name) delete;
      }
      zip.close()
    }  
}

class MediatorActor(boss:BigBossActor, chunkInfo: ChunkInfo) extends Actor{
  print("\n"+chunkInfo)
  var counter:Int = chunkInfo.size
  for (i <- 0 to chunkInfo.size - 1) {new RequestActor(chunkInfo.offset+i,this,boss).start}
  def act{
    while(true){
      receiveWithin(10000){
        case "requestComplete" =>{
          counter = counter - 1
          if (counter == 0) {
            boss ! new ChunkInfo(chunkInfo.size,chunkInfo.offset + chunkInfo.size); return
          }
        }
        case TIMEOUT => boss ! new ChunkInfo(chunkInfo.size,chunkInfo.offset + chunkInfo.size); return
      }
    }
  }
}


class RequestActor(id:Int, mediator: MediatorActor, boss:BigBossActor) extends Actor{
  def act{
    try{
      val url = "http://thepiratebay.se/torrent/" + id
      val connection = new URL(url).openConnection
      connection.setConnectTimeout(2000)
      val header = connection.getHeaderFields().get(null)
      val httpCodeRegex = """(\d{3})""".r
      val number = httpCodeRegex.findFirstIn((""+header).toString()) match{
        case Some("200") =>{
          val pageContent = Source.fromInputStream(connection.getInputStream).getLines.mkString("\n")
          val data = parse(pageContent)
          val out = new java.io.FileWriter(id+".txt")
          out.write(data.title + "\n" + data.hash + "\n" + data.category +"\n\n" + data.nfo)
          out.close
          print (".")
          boss ! new Filename(id+".txt")
          mediator ! "requestComplete"
          return;
        }
        case Some("404") => print("x"); mediator ! "requestComplete";return
        case _ => print("X"); mediator ! "requestComplete"; return
      }
    }
    catch{
      case _ => print("!"); mediator ! "requestComplete"; return
    }
  }
}


class CategoriesActor() extends Actor{
  var categoriesMap = new HashMap[Int, String]
  def act{
    while(true){
      receive{
        case category : Category=> if(!categoriesMap.contains(category.id)) categoriesMap += category.id -> category.name ;
        case "save" =>{
          val out = new java.io.FileWriter("categories.txt")
          val bout = new java.io.BufferedWriter(out);
          for (i <- categoriesMap.keys.toList.sort((a,b)=>(a<b))){
            bout.write(i + " - " + categoriesMap(i))
            bout.newLine
          }
          bout.flush
          out.close
          return
        }
      }
    }
  }
}
