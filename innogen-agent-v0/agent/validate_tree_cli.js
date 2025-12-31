import fs from "fs";
import { validateTree } from "./validator.js";

try {
  // const input = fs.readFileSync(0, "utf-8");
  const input = JSON.stringify({
    type: "text_print",
    value_inputs: {
      TEXT: {
        type: "text_literal",
        fields: { TEXT: "Hello" },
      },
    },
  });

  const tree = JSON.parse(input);
  const errors = validateTree(tree);

  console.log(
    JSON.stringify({
      valid: errors.length === 0,
      errors,
    })
  );
} catch (err) {
  console.log(
    JSON.stringify({
      valid: false,
      errors: [err.message || "Validator crashed"],
    })
  );
}
