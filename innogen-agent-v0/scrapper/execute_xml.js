// window.executeXML = async function (xmlText) {
//   const workspace = Blockly.getMainWorkspace();

//   // 1. Clear canvas
//   workspace.clear();

//   // 2. Inject XML
//   try {
//     const dom = Blockly.utils.xml.textToDom(xmlText);
//     Blockly.Xml.domToWorkspace(dom, workspace);
//   } catch (e) {
//     return {
//       status: "xml_error",
//       error: String(e)
//     };
//   }

//   // 3. Generate Python
//   let pythonCode = "";
//   try {
//     pythonCode = Python.workspaceToCode(workspace);
//   } catch (e) {
//     return {
//       status: "python_generation_error",
//       error: String(e)
//     };
//   }

//   // 4. Return result
//   return {
//     status: "success",
//     python: pythonCode
//   };
// };

window.executeXML = async function (xmlText) {
  if (typeof Blockly === "undefined") {
    console.error("Blockly is not available on the page");
    return {
      status: "blockly_not_loaded",
      error: "Blockly not available",
    };
  }

  const workspace = Blockly.getMainWorkspace();

  if (!workspace) {
    console.error("Blockly workspace not found");
    return {
      status: "workspace_error",
      error: "Main workspace not found",
    };
  }

  // 1️⃣ Clear canvas
  workspace.clear();

  // 2️⃣ Inject XML
  try {
    const dom = Blockly.utils.xml.textToDom(xmlText);
    Blockly.Xml.domToWorkspace(dom, workspace);
  } catch (e) {
    console.error("XML Injection Error:", e);
    return {
      status: "xml_error",
      error: String(e),
    };
  }

  // 3️⃣ Generate Python
  let pythonCode = "";
  try {
    pythonCode = Python.workspaceToCode(workspace);
  } catch (e) {
    console.error("Python Generation Error:", e);
    return {
      status: "python_generation_error",
      error: String(e),
    };
  }

  // 4️⃣ Success
  return {
    status: "success",
    python: pythonCode,
  };
};
