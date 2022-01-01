

### PlantUML Diagramming

We use [PlantUML](https://plantuml.com/) to embed diagrams in README.md and other files. Here’s an example.

![sample PlantUML diagram](https://plantuml.com/imgw/img-35ae0d96da19cd18f27138d3a18af9cd.webp)

To view these diagrams, you will need a Chrome/Edge extension. Here’s how:

1. Download [dist.zip](https://github.com/ctn/plantuml-visualizer/blob/install/dist.zip)
2. Unzip it
3. Open chrome://extensions (or edge://extensions)
4. Turn on “Developer Mode” (a button)
5. Click on “Load Unpacked”
6. Select the unzipped directory, `dist/`

When you are done, reload this page to see the hidden message below.

```
@startuml
left to right direction
Class E 
E --> A
G --> R
A --> T
R --> E
@enduml
```
